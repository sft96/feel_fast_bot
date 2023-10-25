import requests
import probe
from bs4 import BeautifulSoup
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater


def get_new_air_tickets():
    url = 'https://travel.yandex.ru/avia/routes/saint-petersburg--moscow/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    company = soup.find_all('div', class_='EhCXF a-NCA Wu8GK')
    price = soup.find_all('span', class_='bQcBE nb3uL')
    number_of_companies = 7
    results = []
    for i in range(len(company[:number_of_companies])):
        company_name = company[i].text
        price_value = price[i].text
        company_price = f'{company_name} - {price_value}'
        results.append(company_price)
    return results


def air_tickets(update, context):
    chat = update.effective_chat
    air_tickets_data = get_new_air_tickets()
    message = "\n".join(air_tickets_data)
    context.bot.send_message(chat.id, message)


updater = Updater(token=probe.your_token)

url_exchange_rates = "https://www.cbr-xml-daily.ru/latest.js"
url_weather = "https://api.openweathermap.org/data/2.5/weather?q=" + \
              probe.city + \
              "&units=metric&lang=ru&appid="+probe.weather_api_key


def get_new_exchange_rates():
    currency_rounding = 4
    response = requests.get(url_exchange_rates).json()
    actual_date = response["date"]
    reference_currency = response["base"]
    new_exchange_rates = (round(response["rates"]["USD"], currency_rounding),
                          round(response["rates"]["EUR"], currency_rounding))
    return (f"Данные актуальны на: {actual_date}, "
            f"Валюта сравнения: {reference_currency}, "
            f"Курсы основных валют: доллар - {new_exchange_rates[0]}, "
            f"евро - {new_exchange_rates[1]}")


def exchange_rates(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat.id, get_new_exchange_rates())


def get_new_weather():
    response = requests.get(url_weather).json()
    temperature = round(response["main"]["temp"])
    temperature_feels = round(response["main"]["feels_like"])
    return (f"Сейчас в городе {probe.city} "
            f"{str(temperature)} °C, ощущается "
            f"как {str(temperature_feels)} °C")


def weather(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat.id, get_new_weather())


def bot_launch(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([["/Курсы валют"], ["/Погода"],
                                 ["/Авиабилеты"]], resize_keyboard=True)
    context.bot.send_message(chat_id=chat.id,
                             text="Спасибо, что включили меня, "
                                  "{}!".format(name), reply_markup=button)


updater.dispatcher.add_handler(CommandHandler("start", bot_launch))
updater.dispatcher.add_handler(CommandHandler("exchange_rates",
                                              exchange_rates))
updater.dispatcher.add_handler(CommandHandler("weather", weather))
updater.dispatcher.add_handler(CommandHandler("air_tickets", air_tickets))

updater.start_polling()
updater.idle()
