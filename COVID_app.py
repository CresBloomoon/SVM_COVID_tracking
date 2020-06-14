import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import matplotlib.style as style
from datetime import date
import matplotlib.dates as dates
from matplotlib.dates import MonthLocator, DateFormatter, WeekdayLocator
from matplotlib.ticker import NullFormatter
import seaborn as sns
today = date.today()
#sns.set_style('whitegrid')
style.use('fivethirtyeight')
plt.rcParams['lines.linewidth'] = 1
dpi = 1000
plt.rcParams['font.size'] = 8
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['axes.labelsize'] = plt.rcParams['font.size']
plt.rcParams['axes.titlesize'] = plt.rcParams['font.size']
plt.rcParams['legend.fontsize'] = plt.rcParams['font.size']
plt.rcParams['xtick.labelsize'] = plt.rcParams['font.size']
plt.rcParams['ytick.labelsize'] = plt.rcParams['font.size']
plt.rcParams['figure.figsize'] = 8, 8

#@st.cache(suppress_st_warning=True)
def plot_county(county):
    county_confirmed = confirmed[confirmed.Admin2.isin(county)]
    #county_confirmed = confirmed[confirmed.Admin2 == county]
    county_confirmed_time = county_confirmed.drop(county_confirmed.iloc[:, 0:12], axis=1).T #inplace=True, axis=1
    county_confirmed_time = county_confirmed_time.sum(axis= 1)
    county_confirmed_time = county_confirmed_time.reset_index()
    county_confirmed_time.columns = ['date', 'cases']
    county_confirmed_time['Datetime'] = pd.to_datetime(county_confirmed_time['date'])
    county_confirmed_time = county_confirmed_time.set_index('Datetime')
    del county_confirmed_time['date']
    #print(county_confirmed_time.head())
    incidence= pd.DataFrame(county_confirmed_time.cases.diff())
    incidence.columns = ['incidence']
    incidence[incidence.incidence < 0] = 0
    
    #temp_df_time = temp_df.drop(['date'], axis=0).T #inplace=True, axis=1
    county_deaths = deaths[deaths.Admin2.isin(county)]
    population = county_deaths.Population.values.sum()
    
    del county_deaths['Population']
    county_deaths_time = county_deaths.drop(county_deaths.iloc[:, 0:11], axis=1).T #inplace=True, axis=1
    county_deaths_time = county_deaths_time.sum(axis= 1)
    
    county_deaths_time = county_deaths_time.reset_index()
    county_deaths_time.columns = ['date', 'deaths']
    county_deaths_time['Datetime'] = pd.to_datetime(county_deaths_time['date'])
    county_deaths_time = county_deaths_time.set_index('Datetime')
    del county_deaths_time['date']
    
    cases_per100k  = ((county_confirmed_time)*100000/population)
    cases_per100k.columns = ['cases per 100K']
    cases_per100k['rolling average'] = cases_per100k['cases per 100K'].rolling(7).mean()
    
    deaths_per100k  = ((county_deaths_time)*100000/population)
    deaths_per100k.columns = ['deaths per 100K']
    deaths_per100k['rolling average'] = deaths_per100k['deaths per 100K'].rolling(7).mean()
    
    
    incidence['rolling_incidence'] = incidence.incidence.rolling(7).mean()
    metric = (incidence['rolling_incidence']*100000/population).iloc[[-1]]
    st.text('Number of new cases averaged over last seven days = %s' %'{:,.1f}'.format(metric.values[0]))
    st.text("Population under consideration = %s"% '{:,.0f}'.format(population))
    st.text("Total cases = %s"% '{:,.0f}'.format(county_confirmed_time.tail(1).values[0][0]))
    st.text("Total deaths = %s"% '{:,.0f}'.format(county_deaths_time.tail(1).values[0][0]))
    #print(county_deaths_time.tail(1).values[0])
    #print(cases_per100k.head())
    fig, ((ax4, ax3),(ax1, ax2)) = plt.subplots(2,2, figsize=(8,6))
    
    
    lw = 2
    county_confirmed_time.plot(ax = ax1,  lw=lw, color = '#377eb8')
    county_deaths_time.plot(ax = ax1,  lw=lw, color = '#e41a1c')
    ax1.set_xlabel('Time') 
    ax1.set_ylabel('Number of individuals')
    
    
    cases_per100k['cases per 100K'].plot(ax = ax2,  lw=lw, linestyle='--', color = '#377eb8')
    cases_per100k['rolling average'].plot(ax = ax2, lw=lw, color = '#377eb8')
    
    deaths_per100k['deaths per 100K'].plot(ax = ax2,  lw=lw, linestyle='--', color = '#e41a1c')
    deaths_per100k['rolling average'].plot(ax = ax2, lw=lw, color = '#e41a1c')
    
    ax2.set_xlabel('Time')
    ax2.set_ylabel('per 100 thousand')
    
    """Third axis plotting"""
    incidence.incidence.plot(kind ='bar', ax = ax3, width=1)
    ax3.set_xticklabels(incidence.index.strftime('%b %d'))
    for index, label in enumerate(ax3.xaxis.get_ticklabels()):
        if index % 7 != 0:
            label.set_visible(False)
    for index, label in enumerate(ax3.xaxis.get_major_ticks()):
        if index % 7 != 0:
            label.set_visible(False)
    
    (incidence['rolling_incidence']*100000/population).plot(ax = ax4, lw = lw)
    ax4.axhline(y = 5,  linewidth=2, color='r', ls = '--', label="Threshold for Phase 2:\nInitial re-opening")
    ax4.axhline(y = 1,  linewidth=2, color='b', ls = '--', label="Threshold for Phase 3:\nEconomic recovery")
    ax4.legend(fontsize = 10)
    if (incidence['rolling_incidence']*100000/population).max()< 5.5:
        ax4.set_ylim(0,5.5)
    
    #print(metric)
    
    #incidence['rolling_incidence']
    #ax3.grid(which='both', alpha=1)
    ax1.set_title('(C) Cumulative cases and deaths')
    ax2.set_title('(D) Cumulative cases and deaths per 100k')
    ax3.set_title('(B) Daily incidence (new cases)')
    ax4.set_title('(A) Weekly rolling mean of incidence per 100k')
    ax3.set_ylabel('Number of individuals')
    ax4.set_ylabel('per 100 thousand')
    if len(county)<6:
        plt.suptitle('Current situation of COVID-19 cases in '+', '.join(map(str, county))+' county ('+ str(today)+')')
    else:
        plt.suptitle('Current situation of COVID-19 cases in specified region of California ('+ str(today)+')')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    #st.plotly_chart(fig)
    st.pyplot()

@st.cache
def get_data():
    US_confirmed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
    US_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv'
    confirmed = pd.read_csv(US_confirmed)
    deaths = pd.read_csv(US_deaths)
    return confirmed, deaths

confirmed, deaths = get_data()

st.sidebar.markdown('## **EpiCenter for Disease Dynamics**') 
st.sidebar.markdown('**One Health Institute  School of Veterinary Medicine   UC Davis**') 
st.sidebar.markdown("# Metrics for phased reopening")
st.sidebar.markdown("https://www.covidlocal.org/metrics/")
st.sidebar.markdown('For additional information  please contact *epicenter@ucdavis.edu*  https://ohi.vetmed.ucdavis.edu/centers/epicenter-disease-dynamics')
st.sidebar.markdown('## Select counties of interest')
CA_counties = confirmed[confirmed.Province_State == 'California'].Admin2.unique().tolist()
COUNTIES_SELECTED = st.sidebar.multiselect('Select countries', CA_counties, default=['Yolo'])
st.sidebar.markdown("One of the key metrics for which data are widely available is the estimate of **daily new cases per 100,000 population**. Here, in following graphics, we will track")
st.sidebar.markdown("(A) Estimates of daily new cases per 100,000 population (averaged over last seven days)")
st.sidebar.markdown("(B) Daily incidence (new cases)")
st.sidebar.markdown("(C) Cumulative cases and deaths")
st.sidebar.markdown("(D) Cumulative cases and deaths per 100,000 population.")
st.sidebar.markdown("Data source: Data for cases are procured automatically from **COVID-19 Data Repository by the Center for Systems Science and Engineering (CSSE) at Johns Hopkins University**.")
st.sidebar.markdown("he data is updated at least once a day or sometimes twice a day in the COVID-19 Data Repository.  https://github.com/CSSEGISandData/COVID-19")
st.sidebar.text('Report updated on '+ str(today))
st.markdown(COUNTIES_SELECTED)
plot_county(COUNTIES_SELECTED)


st.markdown("## Tri-county area (Yolo, Sacramento, Solano)")
plot_county(['Yolo', 'Solano', 'Sacramento'])

st.markdown("## Yolo")
plot_county(['Yolo'])

st.markdown("## Sacramento")
plot_county(['Sacramento'])

st.markdown("## Solano")
plot_county(['Solano'])

st.markdown("## State of California")
plot_county(confirmed[confirmed.Province_State == 'California'].Admin2.unique().tolist())





