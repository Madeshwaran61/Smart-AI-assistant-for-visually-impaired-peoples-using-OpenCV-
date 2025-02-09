import requests

class Weather:
    def __init__(self, engine):
        self.api_key = "2472b586acf6fb1152123eee8db7e3de"
        self.engine = engine

    def get_weather(self, city):
        url = f"http://api.weatherstack.com/current?access_key={self.api_key}&query={city}"
        response = requests.get(url)
        data = response.json()
        if 'current' in data:
            weather = data['current']['weather_descriptions'][0]
            temperature = data['current']['temperature']
            humidity = data['current']['humidity']
            wind_speed = data['current']['wind_speed']
            speech = f"The weather in {city} is {weather}. The temperature is {temperature} degrees Celsius. The humidity is {humidity} percent. The wind speed is {wind_speed} kilometers per hour."
            print(speech)
            return speech
        else:
            print("Unable to retrieve weather details.")
            self.engine.say("Unable to retrieve weather details.")
