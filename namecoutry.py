import xml.etree.ElementTree as ET
import requests
import mysql.connector


database = mysql.connector.connect(
  host="127.0.0.1",
  user="user1",
  port=3306,
  password="password",
  #A user account allowing any user from localhost to connect is present. This will prevent other users from
)
databaseCursor = database.cursor()


databaseCursor.execute("CREATE DATABASE IF NOT EXISTS db_countries")
databaseCursor.execute("USE db_countries")


databaseCursor.execute("""CREATE TABLE IF NOT EXISTS countries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255),
                    capital VARCHAR(255),
                    currency VARCHAR(3),
                    phone_code VARCHAR(10)
                    )""")

url = "http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?op=FullCountryInfoAllCountries"

payload = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <FullCountryInfoAllCountries xmlns="http://www.oorsprong.org/websamples.countryinfo">
    </FullCountryInfoAllCountries>
  </soap:Body>
</soap:Envelope>"""

headers = {
    'Content-Type': 'text/xml; charset=utf-8'
}
response = requests.request("POST", url, headers=headers, data=payload)
#print(response)
root = ET.fromstring(response.text)

namespaces = {
    'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
    'ns': 'http://www.oorsprong.org/websamples.countryinfo'
}

countries = root.findall('.//ns:FullCountryInfoAllCountriesResponse/ns:FullCountryInfoAllCountriesResult/ns:tCountryInfo', namespaces)

for country in countries:
    country_name = country.find('ns:sName', namespaces).text
    country_capital = country.find('ns:sCapitalCity', namespaces).text
    country_currency = country.find('ns:sCurrencyISOCode', namespaces).text
    country_phone = country.find('ns:sPhoneCode', namespaces).text
    country_continent = country.find('ns:sContinentCode', namespaces).text
    country_flag = country.find('ns:sCountryFlag', namespaces).text

    #country_continent = country_continent.text if country_continent is not None else None

    languages = country.findall('.//ns:Languages/ns:tLanguage', namespaces)
    language_list = [(lang.find('ns:sISOCode', namespaces).text, lang.find('ns:sName', namespaces).text) for lang in languages]

    try:
        sql = "INSERT INTO countries (name, capital, currency, phone_code) VALUES (%s, %s, %s, %s)"
        val = (country_name, country_capital, country_currency, country_phone)
        databaseCursor.execute(sql, val)
        database.commit()
        print(f"Country: {country_name}, Capital: {country_capital}, Currency: {country_currency}, PhoneCode: {country_phone}, Continent: {country_continent}")
        # Print languages
        print("Languages:")
        for iso_code, name in language_list:
            print(f"  ISO Code: {iso_code}, Name: {name}")
        print()
    except mysql.connector.Error as err:
        print("Error:", err)

database.close()
