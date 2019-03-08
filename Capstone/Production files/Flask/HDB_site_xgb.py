from flask import Flask,render_template,session,redirect,url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import (StringField, BooleanField,DateTimeField,RadioField,SelectField,
                    TextField,TextAreaField,SubmitField)

from wtforms.validators import DataRequired

from get_geodata_xgb import get_loc_prediction

app = Flask(__name__)

app.config['SECRET_KEY']='key'

class InfoForm(FlaskForm):

    address = StringField('Address:', validators = [DataRequired()] )
    town = SelectField('HDB Town',
                        choices=[('ANG MO KIO','ANG MO KIO'),
                        ('BEDOK','BEDOK'),('BISHAN','BISHAN'),
                        ('BUKIT BATOK','BUKIT BATOK'),('BUKIT MERAH','BUKIT MERAH'),
                        ('BUKIT PANJANG','BUKIT PANJANG'),('BUKIT TIMAH','BUKIT TIMAH'),
                        ('CENTRAL AREA','CENTRAL AREA'),('CHOA CHU KANG','CHOA CHU KANG'),
                        ('CLEMENTI','CLEMENTI'),('GEYLANG','GEYLANG'),
                        ('HOUGANG','HOUGANG'),('JURONG EAST','JURONG EAST'),
                        ('JURONG WEST','JURONG WEST'),('KALLANG/WHAMPOA','KALLANG/WHAMPOA'),
                        ('MARINE PARADE','MARINE PARADE'),('PASIR RIS','PASIR RIS'),
                        ('PUNGGOL','PUNGGOL'),('QUEENSTOWN','QUEENSTOWN'),
                        ('SEMBAWANG','SEMBAWANG'),('SENGKANG','SENGKANG'),
                        ('SERANGOON','SERANGOON'),('TAMPINES','TAMPINES'),
                        ('TOA PAYOH','TOA PAYOH'),('WOODLANDS','WOODLANDS'),
                        ('YISHUN','YISHUN')], render_kw={"placeholder":"test"})

    flat_model = SelectField('Flat Model',
                        choices= [('New Generation','New Generation'),
                        ('Model A','Model A'), ('Model A2','Model A2'),('Model A-Maisonette','Model A-Maisonette'),
                        ('Standard','Standard'), ('Simplified','Simplified'),('Improved','Improved'),
                        ('Apartment','Apartment'),('Premium Apartment','Premium Apartment'), ('Premium Apartment Loft','Premium Apartment Loft'),
                        ('Type S1','Type S1'), ('Type S2','Type S2'),
                        ('2-room','2-room'),('Adjoined flat','Adjoined flat'), ('Multi Generation','Multi Generation'),
                        ('Terrace','Terrace'), ('DBSS','DBSS'),
                        ('Maisonette','Maisonette'),('Premium Maisonette','Premium Maisonette'), ('Improved-Maisonette','Improved-Maisonette')])

    floor_area = StringField('Floor Area', validators = [DataRequired()])

    storey = StringField('Storey', validators = [DataRequired()])

    lease_remaining = StringField('Years of Lease Remaining', validators = [DataRequired()])

    submit = SubmitField('Submit')



@app.route('/',methods=['GET','POST'])
def index():
    form = InfoForm()

    if form.validate_on_submit():
        session['address'] = form.address.data
        session['town'] = form.town.data
        session['flat_model'] = form.flat_model.data
        session['floor_area'] = form.floor_area.data
        session['storey'] = form.storey.data
        session['lease_remaining'] = form.lease_remaining.data

        return redirect(url_for('thankyou'))

    return render_template('HDB_home.html',form=form)

@app.route('/thankyou')
def thankyou():

    #Retrieve Latitude and longitude of house
    user_add, prediction, latest_sales_500m = get_loc_prediction(session['address'],session['town'],
                                                session['flat_model'],session['floor_area'],
                                                session['storey'],session['lease_remaining'])

    return render_template('HDB_thankyou.html',prediction=prediction,user_add=user_add,tables=[latest_sales_500m.to_html(index=False)])

if __name__ == '__main__':
    app.run(debug=True)
