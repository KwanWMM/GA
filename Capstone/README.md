# Capstone Project on Determining HDB Resale Prices 
(Note: Some of the pcikeld models are not uploaded as they exceed GitHub's size limit.)

## Introduction  
Housing prices are a great concern to many people, your first HDB flat would likely wipe out your CPF savings and take several years to pay off. Should the need to move arise, it would be a tricky case of balancing between the price of a new house, trying to get the most out of selling your current house, as well as the hassle of moving and renovating. 
<br>
Hence,I wanted to build a model that would help people price their resale flats.

## Approach

<ul> 
    <li>Exploring the data</li>
    <li>Preliminary Modelling</li>
    <li>Feature Engineering</li>
    <li>Modelling</li>
    <li>Deployment (local)</li>
</ul>
    
## Initia Dataset and Preliminary Modelling
Using data from data.gov.sg, I started with a dataset of flats sold between January 2015 and the end of 2018. Given the timeframe of this project, I chose not to use data that was available from earlier periods as that would also introduce a time series problem of accounting for inflation. In addition, I planned to use geodata to supplement the data obtained about the flats, but going too far back would increase the inaccuracy of the geodata retrieved (amentites retrieved might not have been present during that time period)
<br>
<br>
I used Linear Regression (high interpretability and relatively computational inexpensive compared to other models, therefore easier to scale and quick to compute for deployment) and Random Forests (non-parametric since many of the features used probably would not share a linear relationship with resale price, reduced overfitting compared to Decision Trees)
<br>
<br>
The evaluation metric I decided on was root mean squared error (RMSE) as it penalized larger errors more heavily, as opposed to just looking at mean errors. The target was to get the RMSE below \\$40,000, as that was less than ten percent of the median of \\$400,000 (mean was \\$440,000, so I chose median as it would be stricter).

## Feature Engineering
Amenities that I used to supplement the original dataset were from three broad categories of transport, schools and others.
<br>
The features I eventually settled on were:
    <ul> 
        <li>Distance to closest MRT</li>
        <li>Name of closest MRT</li>
        <li>Number of hawker centres within 1km</li>
        <li>Number of supermarkets within 1km</li>
        <li>Number of schools within 2km</li>
        <li>Number of SAP schools within 2km</li>
        <li>Number of IP schools within 2km</li>
        <li>Number of Autonomous schools within 2km</li>
        <li>Number of GEP schools within 2km</li>
    </ul>

Other than for MRT stations, I choose the number of amenities within a certain distance as you probably wouldn't be so concerned about the distance to the closest school/hawker centre, but would likely regard it to be a better location if there are a greater number of them (with a greater number, there is also a greater probability of one or several that you prefer).  

## Limitations
There are several key factors that were unable to be captured, such as the condition of the flat at time of sale, as well as the urgency of sale/purchase by the buyer and seller, would could have a considerable impact on the sale prices. The resale prices used are prices as per registration of selling of the flat and there may be some variation for the final resale price decided between the buyer and seller. Prices used are also the nominal price, as the HDB resale index has been relatively stable over the period the data covers. As the flats considered were over a span of three years, the geodata may also have some inaccuracies (opening and closing of supermarkets, schools moving) though they should be minimal.

## Further Modelling
Linear Regression (with regularisation) was not a suitable model, as the plot of residuals against actual price showed great bias for flats beyond about \\$600,000, constantly underpredicting the prices.
Using amenities within 2km and a Random Forest Model, I was able to bring down the initial RMSE from \\$50,000 to about \\$34,500. However, it showed high variance when cross validating the training data. I then looked at using XGBoost. Eventually, it boiled down settled to two different XGBoost models that had a slightly lower RMSE and  significantly lower variance.
<br>
<br>
I considered a minimalist XGBoost model by removing all features that may have redundant information, and used only the flat's latitude and longitude as a proxy for amenities. In other words, the value related to the latitude and longitude is due to what can be found close to that location, not that the numbers of latitude nad longitude are particularly valuable.
<br>
The other XGBoost model was using the selected features mentioned in the previous section (having amenities as explicit features).
<br>
Both models performed rather similarly on the final test set but the minimalist model had significantly lower variance and would likely generalise better. However, the issue with the model was that it can only be used over shorter periods of time. The model would not be able to differentiate between flats sold prior to and after improvement of amenities (eg. upcoming HDB towns). However, if explicit information of amenities (as of time of sale) could be recorded, the XGBoost model using amenities can draw on greater years of data and potentially do better in the long run.
<br>
From the minimalist model, location (latitude nad longitude) had a more significant impact than the floor area or remaining lease of a house, which showed more important amenities are when it comes to considering a house. From the model with amenties explicitly stated, the distance from MRT was a more significant factor than remaining lease, while floor area was the most significant.

## Deployment
To get a better understanding of deployment, I learnt about Flask, Bootstrap, HTML, CSS to build a site where users could key in the details of their flat and receive a suggested resale price, as well a a table of flats sold within 500m of their flat. The table would provide them a better context of the price suggested, as well as allow them to make adjustments to the suggested price based other factors such as the condition of their house. I did not deploy the model online as the API I used for geodata only allows for 60 requests per minute (it would be relatively easy to crash it) and upon considering the time spent on QA to consider how different values and misspellings might crash it, I felt the time would better be invested in further studying of deep learning and other projects instead.