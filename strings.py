def find_train_form_text(form):
    text = f"""
Дата отправления: {form['date']}
Номер поезда: {form['train']}
"""
    return text