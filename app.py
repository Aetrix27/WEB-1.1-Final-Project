from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from datetime import datetime
import calendar
import os
from dotenv import load_dotenv

# Written with help from https://www.guru99.com/calendar-in-python.html

############################################################
# SETUP
############################################################



############################################################
# ROUTES
############################################################

def create_app():

    app = Flask(__name__)
    load_dotenv()

    #secret = os.getenv('MONGO_PASS')
    #secret = os.getenv('SECRET_KEY')
    host = os.environ.get('MONGODB_HOST')
    app.config["MONGO_URI"] = host

    mongo = PyMongo(app)

    
# Send a ping to confirm a successful connection

    @app.route('/')
    def events_list():
        """Display the events list page."""
        today = datetime.today()
        current_month = today.strftime('%B')

        # Extract the current year and month
        current_year = today.strftime("%Y")
        c = calendar.TextCalendar(calendar.SUNDAY)
        days = c.itermonthdays(2025, today.month)
        calendar_days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat']
        events_data = mongo.db.events.find({})
        current_month_int = today.month
        days_list = []
        count=0
        for i in events_data:
            days_list.append([i["day_chosen"], i["_id"],i["photo_url"],i["event_name"]])
            count+=1
        print(days_list[0][0])
        first_day_of_month = datetime(int(current_year), current_month_int, 1)

        # Get the day of the week (0 = Monday, 1 = Tuesday, ..., 6 = Sunday)

        #day_one = int(first_day_of_month.strptime("%d")+1)
        day_one = int(first_day_of_month.weekday() + 1)


        context = {
            'events': days_list,
            'c': c,
            'calendar_days': calendar_days,
            'current_month': current_month,
            'days': days,
            'eventsPresent': True,
            'day_one': day_one

        }

        return render_template('events_list.html', **context)
       

    @app.route('/profile')
    def about():
        """Display the profile page."""

        return render_template('detail.html')


    @app.route('/create/<in_day>', methods=['GET', 'POST'])
    def create(in_day):
        """Display the event creation page & process data from the event form."""
        event = request.form.get('event_name')
        photo_url = request.form.get('photo_url')
        location = request.form.get('location')
        description = request.form.get('description')

        if request.method == 'POST':
            date_created = request.form.get('date_created')
            date_obj = datetime.strptime(date_created, '%Y-%m-%d')
            date_in_days = date_obj.strftime('%d')

            new_event = {
                'event_name': event,
                'photo_url': photo_url,
                'day_chosen': int(date_in_days),
                'date_created': date_created,
                'location': location,
                'description': description
            }

            result = mongo.db.events.insert_one(new_event)
            inserted_id = result.inserted_id

            return redirect(url_for('detail', event_id=inserted_id))
        else:
            if int(in_day) < 10:
                date = datetime.now()
                date=date.replace(day=int(in_day))
                date.strftime(f'%Y-%m-%d')
            elif int(in_day) >= 10:
                date = datetime.now()
                date=date.replace(day=int(in_day))
                date.strftime(f'%Y-%m-%d')

            context = {
                'day_in': date

            }

            return render_template('create.html', **context)


    @app.route('/event/<event_id>')
    def detail(event_id):
        """Display the event detail page & process data from the profile form."""

        event_to_show = mongo.db.events.find_one({
            "_id": ObjectId(event_id)
        })

        profiles = mongo.db.profiles.find({
            "event_id": ObjectId(event_id)
        })

        context = {
            'event': event_to_show,
            'profiles': profiles,
            'event_id': ObjectId(event_id)

        }

        return render_template('detail.html', **context)


    @app.route('/profile/<event_id>', methods=['POST'])
    def profile(event_id):
        """Display the event detail page & process data from the profile form."""

        date_created = request.form.get("date_created")
        profile_name = request.form.get("profile_name")
        number_attending = request.form.get("number_attending")
        time = request.form.get("time")

        new_profile = {
            'number_attending': number_attending,
            'date_created': date_created,
            'event_id': ObjectId(event_id),
            'profile_name': profile_name,
            'time': time

        }

        mongo.db.profiles.insert_one(new_profile)

        return redirect(url_for('detail', event_id=event_id))


    @app.route('/edit/<event_id>', methods=['GET', 'POST'])
    def edit(event_id):
        """Shows the edit page and accepts a POST request with edited data."""
        if request.method == 'POST':
            event = request.form.get('event_name')
            photo_url = request.form.get('photo_url')
            date_created = request.form.get('date_created')
            location = request.form.get('location')
            description = request.form.get('description')

            mongo.db.events.update_one({
                '_id': ObjectId(event_id)
            },
                {
                '$set': {
                    '_id': ObjectId(event_id),
                    'event_name': event,
                    'date_created': date_created,
                    'photo_url': photo_url,
                    'location': location,
                    'description': description
                }
            })

            return redirect(url_for('detail', event_id=event_id))
        else:
            event_to_show = mongo.db.events.find_one({
                '_id': ObjectId(event_id)
            })

            context = {
                'event': event_to_show
            }

            return render_template('edit.html', **context)


    @app.route('/delete/<event_id>', methods=['POST'])
    def delete(event_id):
        mongo.db.events.delete_one({
            '_id': ObjectId(event_id)
        })
        mongo.db.profiles.delete_many({
            'event_id': ObjectId(event_id)
        })

        return redirect(url_for('events_list'))


    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
