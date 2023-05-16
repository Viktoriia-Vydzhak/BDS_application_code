"""
This code is based on the final project for the "Python Data Visualization"
course on Coursera. I was working from a template which included signatures
for the functions (which made machine grading possible), but no bodies of
functions. So the body of each function here was written by me.

The purpose of this code is to plot GDP data for a given year on the world map.
Here, country codes are used to extract data for each country from the file with
GDP data obtained from World Bank site (and slightly modified). Using country codes
allows obtaining data for more countries than using country names, and the purpose
of build_country_code_converter() and reconcile_countries_by_code() functions is
actually to map the country codes used by the plotting library to those used in the
GDP data file.
"""

import csv
import math
import pygal

def read_csv_as_nested_dict(filename, keyfield, separator, quote):
    """
    Inputs:
      filename  - Name of CSV file
      keyfield  - Field to use as key for rows
      separator - Character that separates fields
      quote     - Character used to optionally quote fields

    Output:
      Returns a dictionary of dictionaries where the outer dictionary
      maps the value in the key_field to the corresponding row in the
      CSV file.  The inner dictionaries map the field names to the
      field values for that row.
    """
    output_dict={}
    with open(filename, newline='') as csvfile:
        csvreader=csv.DictReader(csvfile, delimiter=separator, quotechar=quote)
        for row in csvreader:
            row_name=row[keyfield]
            output_dict[row_name]=row
    return output_dict

def build_country_code_converter(codeinfo):
    """
    Inputs:
      codeinfo      - A country code information dictionary

    Output:
      A dictionary whose keys are plot country codes and values
      are world bank country codes, where the code fields in the
      code file are specified in codeinfo.
    """
    output_dict={}
    code_dict=read_csv_as_nested_dict(codeinfo["codefile"], codeinfo["plot_codes"], codeinfo["separator"], codeinfo["quote"])
    for code, values in code_dict.items():
        output_dict[code]=values[codeinfo["data_codes"]]
    return output_dict


def reconcile_countries_by_code(codeinfo, plot_countries, gdp_countries):
    """
    Inputs:
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary whose keys are plot library country codes
                       and values are the corresponding country name
      gdp_countries  - Dictionary whose keys are country codes used in GDP data

    Output:
      A tuple containing a dictionary and a set.  The dictionary maps
      country codes from plot_countries to country codes from
      gdp_countries.  The set contains the country codes from
      plot_countries that did not have a country with a corresponding
      code in gdp_countries.

      Note that all codes should be compared in a case-insensitive
      way.  However, the returned dictionary and set should include
      the codes with the exact same case as they have in
      plot_countries and gdp_countries.
    """
    output_dict={}
    output_set=set()
    code_converter=build_country_code_converter(codeinfo)
    lowercase_code_converter={}
    for code, match in code_converter.items():
        lowercase_code_converter[code.lower()]=match.lower()
    lowercase_plot_codes={}
    for key in plot_countries:
        lowercase_plot_codes[key.lower()]=key
    lowercase_gdp_codes={}
    for gdpcode in gdp_countries:
        lowercase_gdp_codes[gdpcode.lower()]=gdpcode
    for lowercode, normalcode in lowercase_plot_codes.items():
        if lowercode in lowercase_code_converter:
            gdpmatch=lowercase_code_converter[lowercode]
            if gdpmatch in lowercase_gdp_codes:
                normalgdp=lowercase_gdp_codes[gdpmatch]
                output_dict[normalcode]=normalgdp
            else:
                output_set.add(normalcode)
        else:
            output_set.add(normalcode)
    return (output_dict, output_set)


def build_map_dict_by_code(gdpinfo, codeinfo, plot_countries, year):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary mapping plot library country codes to country names
      year           - String year for which to create GDP mapping

    Output:
      A tuple containing a dictionary and two sets.  The dictionary
      maps country codes from plot_countries to the log (base 10) of
      the GDP value for that country in the specified year.  The first
      set contains the country codes from plot_countries that were not
      found in the GDP data file.  The second set contains the country
      codes from plot_countries that were found in the GDP data file, but
      have no GDP data for the specified year.
    """
    output_dict={}
    set1=set()
    set2=set()
    gdp_dict=read_csv_as_nested_dict(gdpinfo["gdpfile"], gdpinfo["country_code"], gdpinfo["separator"], gdpinfo["quote"])
    country_codes=reconcile_countries_by_code(codeinfo, plot_countries, gdp_dict)
    codes_dict=country_codes[0]
    for plotcode, gdpcode in codes_dict.items():
        gdp_country=gdp_dict[gdpcode]
        if year in gdp_country and gdp_country[year]!='':
            output_dict[plotcode]=math.log(float(gdp_country[year]), 10)
        else:
            set2.add(plotcode)
    set1=country_codes[1]
    return (output_dict, set1, set2)

def render_world_map(gdpinfo, codeinfo, plot_countries, year, map_file):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary mapping plot library country codes to country names
      year           - String year of data
      map_file       - String that is the output map file name

    Action:
      Creates a world map plot of the GDP data in gdp_mapping and outputs
      it to a file named by svg_filename.
    """
    map_info=build_map_dict_by_code(gdpinfo, codeinfo, plot_countries, year)
    gdp_dict=map_info[0]
    missing_countries=map_info[1]
    missing_gdp=map_info[2]
    worldmap=pygal.maps.world.World()
    worldmap.title='GDP data per country at given year (log scale)'
    worldmap.add('In '+year, gdp_dict)
    worldmap.add('No data', missing_countries)
    worldmap.add('No gdp data for given year', missing_gdp)
    worldmap.render_to_file(map_file)
    return

# Uncomment the code below to test the functions.

# gdpinfo = {
#         "gdpfile": "isp_gdp.csv",
#         "separator": ",",
#         "quote": '"',
#         "min_year": 1960,
#         "max_year": 2015,
#         "country_name": "Country Name",
#         "country_code": "Country Code"}
# codeinfo = {
#         "codefile": "isp_country_codes.csv",
#         "separator": ",",
#         "quote": '"',
#         "plot_codes": "ISO3166-1-Alpha-2",
#         "data_codes": "ISO3166-1-Alpha-3"}
# pygal_countries = pygal.maps.world.COUNTRIES
#  
# render_world_map(gdpinfo, codeinfo, pygal_countries, "1960", "isp_gdp_world_code_1960.svg")
# 
#     
# render_world_map(gdpinfo, codeinfo, pygal_countries, "1980", "isp_gdp_world_code_1980.svg")
# 
#     
# render_world_map(gdpinfo, codeinfo, pygal_countries, "2000", "isp_gdp_world_code_2000.svg")
# 
#     
# render_world_map(gdpinfo, codeinfo, pygal_countries, "2010", "isp_gdp_world_code_2010.svg")
