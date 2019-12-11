'''
COMP9321 2019 Term 1 Assignment Two Code Template
Student Name:
Student ID:
'''
import requests
import sqlite3
import datetime
from flask import Flask
from flask_restplus import Resource, Api, fields, reqparse
import json




def create_db(db_file):
    '''
    use this function to create a db, don't change the name of this function.
    db_file: Your database's name.
    '''
    #connect to databsae 'data.db'
    conn = sqlite3.connect(db_file)
    conn.execute(""" CREATE TABLE IF NOT EXISTS INDICATORS (
                                                    collection_id integer PRIMARY KEY AUTOINCREMENT,
                                                    indicator text NOT NULL,
                                                    indicator_value text,
                                                    creation_time text,
                                                    entries text
                                                ); """)
    conn.close()

app = Flask(__name__)
api = Api(app)

an_indicator = api.model('indicator',{"indicator_id" : fields.String('The indicator_id')})

@api.route('/indicators')
class question_1_3(Resource):
    #Q3
    def get(self):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT collection_id,creation_time,indicator FROM INDICATORS''')
        total = []
        for i in cursor.fetchall():
            one_collection = dict()
            one_collection['location'] = '/indicators/{}'.format(i[0])
            one_collection['collection_id'] = str(i[0])
            one_collection['creation_time'] = i[1]
            one_collection['indicator'] = i[2]
            total.append(one_collection)
        conn.close()
        return total, 200
    #Q1
    @api.expect(an_indicator)
    def post(self):
        indicator = api.payload
        # create table and store data
        # build data dict firstly.
        url = "http://api.worldbank.org/v2/countries/all/indicators/" + indicator["indi
        if len(get_data) == 1:
            return 'Invalid attempts', 404
        # json.loads(get_data)
        # make "entries"cator_id"] + "?date=2013:2018&format=json&per_page=100"
        get_data = requests.get(url)
        get_data = get_data.json()
        entries = []
        for i in get_data[1]:
            entry = dict()
            entry['country'] = i['country']['value']
            entry['date'] = i['date']
            entry['value'] = i['value']
            entries.append(entry)
        # store every values into a_collection(dictionary)
        a_collection = dict()
        a_collection['indicator'] = indicator['indicator_id']
        a_collection['indicator_value'] = get_data[1][0]['indicator']['value']
        a_collection['creation_time'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-7] + 'Z'
        a_collection['entries'] = json.dumps(entries)
        # connect to database
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        # insert data
        cursor.execute('''SELECT COUNT(indicator) FROM INDICATORS WHERE indicator = ('%s')'''%(a_collection['indicator']))
        i = cursor.fetchall()
        # if this indicator has been in the database
        if i[0][0] != 0:
            cursor.execute('''SELECT collection_id,indicator,indicator_value,creation_time FROM INDICATORS WHERE indicator = ('%s')'''%(a_collection['indicator']))
            info = cursor.fetchall()
            a_collection['collection_id'] = info[0][0]
            a_collection['creation_time'] = info[0][3]
            conn.close()
            return {"location": "/indicators/{}".format(a_collection['collection_id']),
                    "collection_id": "{}".format(a_collection['collection_id']),
                    "creation_time": "{}".format(a_collection['creation_time']),
                    "indicator": "{}".format(indicator["indicator_id"])}, 200
        else:
            cursor.execute('''INSERT INTO INDICATORS(indicator,indicator_value,creation_time,entries)
            VALUES(?,?,?,?)''', (a_collection['indicator'], a_collection['indicator_value'], a_collection['creation_time'], a_collection['entries']))
            conn.commit()
            cursor.execute('''SELECT MAX(collection_id) FROM INDICATORS''')
            a_collection['collection_id'] = cursor.fetchall()[0][0]
            conn.close()
            return {"location": "/indicators/{}".format(a_collection['collection_id']),
                    "collection_id": "{}".format(a_collection['collection_id']),
                    "creation_time": "{}".format(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-7] + 'Z'),
                    "indicator": "{}".format(indicator["indicator_id"])}, 201

@api.route('/indicators/<int:collection_id>')
class question_2_4(Resource):
    #Q4
    def get(self, collection_id):
        try:
            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()
            cursor.execute('''SELECT * FROM INDICATORS WHERE collection_id = ('%d')'''%(collection_id))
            i = cursor.fetchall()
            get_collection = dict()
            get_collection['collection_id'] = i[0][0]
            get_collection['indicator'] = i[0][1]
            get_collection['indicator_value'] = i[0][2]
            get_collection['creation_time'] = i[0][3]
            get_collection['entries'] = json.loads(i[0][4])
        except IndexError:
            return 'No collection id', 404
        conn.close()
        return get_collection, 200
    #Q2
    def delete(self, collection_id):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM INDICATORS WHERE collection_id = ('%d')'''%(collection_id))
        conn.commit()
        conn.close()
        return {"message": "Collection = {} is removed from the database!".format(collection_id)}, 200

@api.route('/indicators/<int:collection_id>/<string:year>/<string:country>')
class question_5(Resource):
    #Q5
    def get(self, collection_id, year, country):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT indicator,indicator_value,entries FROM INDICATORS WHERE collection_id = ('%d')'''%(collection_id))
        try:
            i = cursor.fetchall()[0]
        except IndexError:
            return 'Invalid collection id', 404

        conn.close()
        indicator = i[0]
        indicator_value = i[1]
        entries = json.loads(i[2])
        economic = dict()
        for entry in entries:
            if entry['country'] == country and entry['date'] == year:
                economic['collection_id'] = collection_id
                economic['indicator'] = indicator
                economic['country'] = country
                economic['year'] = year
                economic['value'] = indicator_value
        return economic, 200


parser = reqparse.RequestParser()
parser.add_argument('q', type=str, required=True)

@api.route('/indicators/<int:collection_id>/<string:year>')
class question_6(Resource):
    #Q6
    @api.expect(parser, validate=True)
    def get(self, collection_id, year):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT indicator,indicator_value,entries FROM INDICATORS WHERE collection_id = ('%d')''' % (collection_id))
        try:
            i = cursor.fetchall()[0]
        except IndexError:
            return 'No Collection ID', 404
        conn.close()
        indicator = i[0]
        indicator_value = i[1]
        entries = json.loads(i[2])
        entries_without_null = []
        for i in entries:
            if i['value'] is not None and i['date'] == year:
                entries_without_null.append(i)
        entries_without_null.sort(key=lambda entry: entry['value'])
        top_or_bottom = dict()
        top_or_bottom['indicator'] = indicator
        top_or_bottom['indicator_value'] = indicator_value

        parser_args = dict(parser.parse_args())
        if parser_args['q'][:3] == 'top':
            try:
                num = int(parser_args['q'][3:])
                if num <= 0:
                    return 'Invalid query', 404
            except ValueError:
                return 'Invalid query', 404
            # when the required num >= the countries in entries
            if num >= len(entries_without_null):
                top_or_bottom['entries'] = entries_without_null[::-1]
            else:
                top_or_bottom['entries'] = entries_without_null[:-num-1:-1]
            return top_or_bottom, 200
        elif parser_args['q'][:6] == 'bottom':
            try:
                num = int(parser_args['q'][6:])
                if num <= 0:
                    return 'Invalid query', 404
            except ValueError:
                return 'Invalid query', 404
            # when the required num >= the countries in entries
            if num >= len(entries_without_null):
                top_or_bottom['entries'] = entries_without_null
            else:
                top_or_bottom['entries'] = entries_without_null[:num]
            return top_or_bottom, 200
        else:
            return 'Invalid query', 404



if __name__ == '__main__':

    app.run(debug=True)
    create_db('data.db')

