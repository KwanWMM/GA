import pandas as pd
import numpy as np
import json
from geopy.distance import geodesic
import requests
from bs4 import BeautifulSoup

#
def get_loc_prediction(address,town,flat_model,floor_area,storey,lease_remaining):

    #Retrieve lat long data for addressed submitted
    search_query = address
    response = requests.get('https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1'.format(search_query))

    user_add = json.loads(response.text)['results'][0]['ADDRESS']
    latitude = float(json.loads(response.text)['results'][0]['LATITUDE'])
    longitude = float(json.loads(response.text)['results'][0]['LONGITUDE'])
    flat=(latitude, longitude)

    #load the mrt latlong data
    mrt_latlong = pd.read_csv('./csv files/mrt_full.csv',index_col=0)

    #Create a list of MRT stations within 4km (furthest MRT was 3.6KM)
    mrt_in_range = mrt_latlong[(abs(mrt_latlong['Latitude']-latitude)<0.036) & (abs(mrt_latlong['Longitude']-longitude)<0.036)]

    #Iterate through the list of MRT stations within 4KM
    nearest_mrt = None
    mrt_dist = 5
    for index in range(len(mrt_in_range)):
        mrt_lat=mrt_in_range.iloc[index,4]
        mrt_long=mrt_in_range.iloc[index,5]
        mrt=(mrt_lat,mrt_long)
        #If the record the station and distance if the distance is lower than the one before
        distance = geodesic(flat,mrt).km
        if distance < mrt_dist:
            mrt_dist = distance
            nearest_mrt = mrt_in_range.iloc[index,1]

    #load in latlong for other amenities
    sch_latlong = pd.read_csv('./csv files/sch_latlong_corrected.csv',index_col=0)
    hawker_latlong = pd.read_csv('./csv files/hawker_latlong.csv',index_col=0)
    sm_latlong = pd.read_csv('./csv files/sm_latlong.csv',index_col=0)
    sap_sch_latlong = pd.read_csv('./csv files/sap_sch_latlong.csv',index_col=0)
    autonomous_ind_latlong = pd.read_csv('./csv files/autonomous_ind_latlong.csv',index_col=0)
    gifted_ind_latlong = pd.read_csv('./csv files/gifted_ind_latlong.csv',index_col=0)
    ip_ind_latlong = pd.read_csv('./csv files/ip_ind_latlong.csv',index_col=0)

    #Create dictionary to store search results
    amenities_dict={'num_sch':0,'num_hawkers':0,'num_sm':0,'num_sap':0,'num_autonomous':0,'num_gifted':0,'num_ip':0}

    #Create a list to iterate trhough, each entry in the format of [amenity key,amneity DataFrame name,distance to check]
    amenities = [['num_sch',sch_latlong,2],['num_hawkers',hawker_latlong,1],
                 ['num_sm',sm_latlong,1],['num_sap',sap_sch_latlong,2],
                 ['num_autonomous',autonomous_ind_latlong,2],['num_gifted',gifted_ind_latlong,2],['num_ip',ip_ind_latlong,2]]


    #Retrieve the number of amenities within given distance
    for amenity in amenities:
            #Subset the DataFrame to a square of side 2*distance
            amenity_in_range = amenity[1][(abs(amenity[1][amenity[1].columns[1]]-latitude)<0.009*amenity[2])
                                            & (abs(amenity[1][amenity[1].columns[2]]-longitude)<0.009*amenity[2])]
            count = 0
            #Check within the subset for amenities within the given distance
            for index in range(len(amenity_in_range)):
                if geodesic(flat,(amenity_in_range.iloc[index,1],amenity_in_range.iloc[index,2])).km < amenity[2]:
                    count+=1
            #Save the count in the results dictionary
            amenities_dict[amenity[0]]=count

    #Load the empty DataFrame and storey selection DataFrame
    entry = pd.read_csv('./csv files/empty_entry.csv',index_col=0)
    storey_select= pd.read_csv('./csv files/storey_select.csv',index_col=0)

    #Assign the retrieved values(amenities)
    entry['schs_2km']=amenities_dict['num_sch']
    entry['hawker_1km']=amenities_dict['num_hawkers']
    entry['supermarket_1km']=amenities_dict['num_sm']
    entry['sap_sch_2km']=amenities_dict['num_sap']
    entry['autonomous_sch_2km']=amenities_dict['num_autonomous']
    entry['gifted_sch_2km']=amenities_dict['num_gifted']
    entry['ip_sch_2km']=amenities_dict['num_ip']

    #Assign the retrieved values(amenities)
    entry['closest_mrt_'+nearest_mrt]=1
    entry['dist_mrt_km']=mrt_dist

    #Assign the retrieved values(flat values keyed in by user)
    entry['town_'+town]=1
    entry['floor_area_sqm']=float(floor_area)
    entry['flat_model_'+flat_model]=1
    entry['remaining_lease']=int(lease_remaining)

    #Convert (user keyed) storey to storey range
    storey = int(storey)

    #Limit the max storey to 51. Higher storeys will be converted to 51
    if storey>51:
        storey=51

    if storey%3==0:
        storey-=1
    entry[storey_select[storey_select['Quotient']==(storey//3)].index]=1

    # Use this loop to print all the values in console for checking
    # for index,col in enumerate(entry.iloc[0]):
    #     print(entry.columns[index],col)

    #import the pickled model
    import pickle
    final_model = pickle.load(open('./csv files/amenities_XGB_model.pickle', 'rb'))

    #Enter flat values into the model and return the predicted price
    predicted_price="{:,}".format(int(final_model.predict(entry.iloc[[0]])))

    #Retrieve flats (within 500m of target flat) previously sold
    house_latlong = pd.read_csv("./csv files/hdb_inc_latlong.csv", index_col=0)

    #subset DataFrame to 1km by 1km square
    flats_500m = house_latlong[(abs(house_latlong['Latitude']-latitude)<0.0045)&(abs(house_latlong['Longitude']-longitude)<0.0045)]
    drop_flats  = []

    #Check for flats in square but outside the 500m radius
    for index in flats_500m.index:
        if geodesic(flat,(flats_500m.loc[index]['Latitude'],flats_500m.loc[index]['Longitude'])).km > 0.5:
            drop_flats.append(index)

    #Drop the flats out of range
    latest_sales_500m = flats_500m.drop(drop_flats,axis=0).iloc[:,:-3].sort_values('month',ascending=False)
    #Drop the lease commencement column
    latest_sales_500m.drop('lease_commence_date',axis=1,inplace=True)
    #Rename columns for easier reading
    latest_sales_500m.columns=['month','town' ,'flat type','block' ,'street name','storey range','floor area sqm','flat model','remaining lease' ,'resale price']

    #Return the retrieved address, predicted price and flats sold within 500m
    return user_add, predicted_price, latest_sales_500m
