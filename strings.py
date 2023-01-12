def find_train_form_text(form):
    text = f"""
Дата отправления: {form['date']}
Номер поезда: {form['train']}
"""
    return text


def places_text(stops, car, car_number, chosen_place):
    chosen_place = chosen_place.zfill(3)
    text = f"Вагон номер: {car_number}\n"

    for stop_id in range(len(stops)):
        temp = f"{stops[stop_id]['station']['name'].lower().capitalize()}"

        if stop_id == len(stops) - 1:
            if chosen_place in car[stop_id - 1]:
                text += '***' + temp + '***'
            else:
                text += temp
            continue

        if stop_id == 0:
            if chosen_place in car[stop_id]:
                temp = '***' + temp + '***'
        else:
            if chosen_place in car[stop_id-1] or chosen_place in car[stop_id]:
                temp = '***' + temp + '***'
        if stop_id != len(stops) - 1:
            temp += ' - '

        text += temp

    return text
