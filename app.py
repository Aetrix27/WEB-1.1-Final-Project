from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
import calendar
from jinja2.ext import do

#Written with help from https://www.guru99.com/calendar-in-python.html

############################################################
# SETUP
############################################################

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/eventsDatabase"
mongo = PyMongo(app)
app.jinja_env.add_extension('jinja2.ext.do')

############################################################
# ROUTES
############################################################

@app.route('/')
def events_list():
    """Display the events list page."""
    today = datetime.today()
    current_month = today.strftime('%B')
    c=calendar.TextCalendar(calendar.SUNDAY)
    days=c.itermonthdays(2025,today.month)
    calendar_days=calendar.day_name
    
    events_data=mongo.db.events.find({})

    context = {
        'events': events_data,
        'c': c,
        'calendar_days' : calendar_days,
        'current_month' : current_month,
        'days' : days,
    }

    return render_template('events_list.html', **context)

@app.route('/profile')
def about():
    """Display the profile page."""
    return render_template('detail.html')

@app.route('/create/<in_day>', methods=['GET', 'POST'])
def create(in_day):
    """Display the event creation page & process data from the event form."""
    event=request.form.get('event_name')
    photo=request.form.get('photo')

    if request.method == 'POST':
        date_created=request.form.get('date_created')
        date_obj = datetime.strptime(date_created, '%Y-%m-%d')
        date_in_days = date_obj.strftime('%-d')
        print(date_in_days)
        
        new_event = {
            'event_name': event,
            'photo_url': photo,
            'day_chosen' : int(date_in_days),
            'date_created' : date_created,
        }
 
        result=mongo.db.events.insert_one(new_event)
        inserted_id=result.inserted_id

        return redirect(url_for('detail', event_id=inserted_id))
    else:
        if int(in_day)<10:
            date=datetime.today().strftime(f'%Y-%m-0%{in_day}')
        elif int(in_day)>=10:
            date=datetime.today().strftime(f'%Y-%m-%{in_day}')
        context={
            'day_in' : date

        }
        print(date)

        return render_template('create.html',**context)

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
    profile_name=request.form.get("profile_name")
    input_string=request.form.get("number_attending")

    new_profile = {
        'number_attending': input_string,
        'date_created': date_created,
        'event_id': ObjectId(event_id),
        'profile_name' : profile_name,
    
    }

    mongo.db.profiles.insert_one(new_profile)

    return redirect(url_for('detail', event_id=event_id))

@app.route('/edit/<event_id>', methods=['GET', 'POST'])
def edit(event_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == 'POST':
        event = request.form.get('event_name')
        photo = request.form.get('photo')
        date_created = request.form.get('date_created')

        mongo.db.events.update_one({
            '_id': ObjectId(event_id)
        },
        {
            '$set': { 
                '_id': ObjectId(event_id),
                'event_name' : event,
                'date_created' : date_created,
                'photo_url' : photo
            }
        })
        
        return redirect(url_for('detail', event_id=event_id))
    else:
        event_to_show=mongo.db.events.find_one({
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

if __name__ == '__main__':
    app.run(debug=True)

