# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 18:08:31 2020

@author: is104
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 16:57:44 2020

@author: ivan.sheng
"""

import numpy as np
import pandas as pd
import os
import copy
import pycountry_convert as pc
from string import punctuation

def formatColNames(data):
    """
    Format column names into requested format: Q#. ([Answer]) [Question]
    
    Parameters:
        data (dataframe): original RAW survey data

    Returns:
        finalColNames (list): map of original RAW column names to requested names.
    """
    replace = ['Open-Ended Response', 'Response']
    replacement = [None,None]

    lookup = data[:1].T.dropna().reset_index(drop=True)
    lookup[1] = np.nan
    c = 1
    for i in range(0,len(lookup)):
        if any(p in lookup[0][i] for p in punctuation):
            lookup[1][i] = 'Q' + str(c) + '. '
            c += 1
        else:
            lookup[1][i] = ''
    
    fillQ = data[:1].T.fillna(method = 'ffill').merge(lookup, on=0)
    category = data[1:2].T
    
    category = category[1].str.replace(r"\(.*\)","").replace(replace, replacement)
    category = ('(' + category.str.strip() + ') ').fillna('')
    finalColNames = (fillQ[1] + category + fillQ[0]).tolist()
    
    return finalColNames

def appendContinentCol(self):
    """
    Maps countries to continents
    
    Parameters:
        self (dataframe): survey data with requested column names
        
    Returns:
        self (dataframe): survey data with requested column names and continent
    
    """
    continent = []
    for country in self['Q1. What is your country of residence?']:
        country_alpha2 = pc.country_name_to_country_alpha2(country)
        continent_alpha2 = pc.country_alpha2_to_continent_code(country_alpha2)
        continent.append(pc.convert_continent_code_to_continent_name(continent_alpha2))
    
    col_idx = self.columns.get_loc('Q1. What is your country of residence?')+1
    self.insert(loc = col_idx, column = 'Q1. Continent', value = continent)
    
    return self

def formatAndEncode(data, combined, order):
    """
    Formats the column names of the original RAW data to requested names.
    combined (dataframe): map of original RAW column names to requested names.
    
    Parameters:
        data (dataframe): original RAW survey data
        combined (dataframe): map of original RAW column names to requested names what will be modified
        order (dataframe): map of original RAW column names to requested names.
        
    Returns:
        formattedData (dataframe): survey data in its final requested format
    """
    
    data = data[2:]
    uniqueAns = data.nunique()

    dropOffcheck = 0
    shift_col = []
    for i in range(10,np.shape(data)[1]):
        if uniqueAns[i] == 1:
            data=pd.get_dummies(data,columns = [i])
            shift_col.append(i)
            dropOffcheck += data.iloc[:,-1]
        #if only 2 unique answers - it's a yes/no
        elif uniqueAns[i] == 2:
            data[i] = data[i].map(dict(Yes=1, No=0))
            
    dropOffcheck = dropOffcheck.to_frame(name = 'Check #')
    dropOffcheck['Drop Off'] = (dropOffcheck['Check #'] == 0).astype(int)
            
    adjust = 0
    for i in shift_col:
        combined.append(combined.pop(i-adjust))
        adjust += 1
    
    data.columns = combined
    formattedData = data[order]
    formattedData = pd.concat([formattedData,dropOffcheck], axis = 1, sort=False).reset_index(drop=True)
    formattedData.drop(columns = ['Email Address','First Name','Last Name','Custom Data 1'], inplace = True)
    
    return formattedData

def main():
    path = 'C:/Users/ivan.sheng/Documents/' #change path
    os.chdir(path)
    rtsd = 'Relationships in Times of Social Distancing  Wave2.xlsx' #replace input file name
    
    data = pd.read_excel(rtsd, header = None, encoding='utf-8')
    
    combined = formatColNames(data)
    order = copy.deepcopy(combined)
    
    formattedData = formatAndEncode(data, combined, order)
    finalData = appendContinentCol(formattedData)
    
    finalData.to_excel('rtsd_tableau_feed_wk2_v2.xlsx') #replace output file name
    
if __name__ == '__main__':
    main()