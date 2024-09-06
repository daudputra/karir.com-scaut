from datetime import datetime

def today():
    today = datetime.today()
    formatted_date = today.strftime("%#d %B %Y")
    return formatted_date