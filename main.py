import streamlit as st
import random
import time
import sqlite3
import os

# Создание или подключение к базе данных
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Создание таблицы пользователей, если она не существует
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    balance INTEGER NOT NULL
)
''')

# Создание таблицы для хранения выбитых предметов
c.execute('''
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    item_name TEXT NOT NULL,
    item_value INTEGER NOT NULL
)
''')
conn.commit()

# Функция для регистрации пользователя
def register_user(name):
    initial_balance = 50  # Начальный баланс
    c.execute("INSERT INTO users (name, balance) VALUES (?, ?)", (name, initial_balance))
    conn.commit()

# Функция для получения баланса пользователя
def get_user_balance(name):
    c.execute("SELECT balance FROM users WHERE name=?", (name,))
    result = c.fetchone()
    return result[0] if result else None

# Функция для обновления баланса пользователя
def update_user_balance(name, new_balance):
    c.execute("UPDATE users SET balance=? WHERE name=?", (new_balance, name))
    conn.commit()

# Функция для сохранения выбитого предмета
def save_item(user_name, item_name, item_value):
    c.execute("INSERT INTO items (user_name, item_name, item_value) VALUES (?, ?, ?)", (user_name, item_name, item_value))
    conn.commit()

# Функция для получения всех выбитых предметов пользователя
def get_user_items(user_name):
    c.execute("SELECT item_name, item_value FROM items WHERE user_name=?", (user_name,))
    return c.fetchall()

# Элементы для игры с шансами
items_with_chances = {
    'image0.webp': (0, 0.5),  # 50% шанс
    'image1.png': (5, 0.2),   # 20% шанс
    'image2.jpg': (15, 0.1),  # 10% шанс
    'image3.webp': (1, 0.008),   # 0,8% шанс
    'image4.webp': (7, 0.005),  # 0,5% шанс
    'image5.webp': (30, 0.001)   # 0,1% шанс
}

def spin_items():
    spin_duration = 3  
    end_time = time.time() + spin_duration
    selected_item = None

    while time.time() < end_time:
        selected_item = random.choices(
            list(items_with_chances.keys()),
            weights=[chance for _, chance in items_with_chances.values()],
            k=1
        )[0]
        time.sleep(0.5)  
    return selected_item

# Навигация по страницам
st.sidebar.title("Навигация")
page = st.sidebar.radio("Выберите страницу:", ["Регистрация", "Вход", "Крутилка", "Профиль"])

# Страница регистрации
if page == "Регистрация":
    st.title("Регистрация")
    name = st.text_input("Введите ваше имя:")

    if st.button("Зарегистрироваться"):
        if name:
            register_user(name)
            st.success(f"Пользователь {name} зарегистрирован с начальным балансом 50!")
        else:
            st.error("Пожалуйста, введите имя.")

# Страница входа
elif page == "Вход":
    st.title("Вход")
    user_name = st.text_input("Введите ваше имя для входа:")

    if st.button("Войти"):
        balance = get_user_balance(user_name)
        if balance is not None:
            st.session_state.user_name = user_name  # Сохраняем имя пользователя в session_state
            st.session_state.balance = balance  # Сохраняем баланс в session_state
            st.success(f"Добро пожаловать, {user_name}! Ваш баланс: {balance} звёзд.")
        else:
            st.error("Пользователь не найден. Пожалуйста, зарегистрируйтесь.")

# Страница крутилки
elif page == "Крутилка":
    st.title("Крутилка")
    
    if 'user_name' in st.session_state:
        st.write(f"Добро пожаловать, {st.session_state.user_name}! Ваш баланс: {st.session_state.balance} звёзд.")

        # Проверка, достаточно ли средств для крутки
        if st.session_state.balance >= 25:

            if 'spin_button_clicked' not in st.session_state:
                st.session_state.spin_button_clicked = False

            if st.session_state.spin_button_clicked:
                st.button("Крутить!", disabled=True)  # Кнопка отключена после нажатия
                with st.spinner("Раскручиваем барабан..."):
                    selected_item = spin_items()
                    st.image(selected_item, width=200)
                    item_value = items_with_chances[selected_item][0]
                    if item_value == 0 or item_value == 5 or item_value == 15:
                        st.write(f"Вы получили {item_value} звёзд")
                    elif item_value == 1:
                        st.write(f"Вы получили подписку на пробив: {item_value} день")
                    else:
                        st.write(f"Вы получили подписку на пробив: {item_value} дней")
                    
                    # Сохраняем выбитый предмет
                    save_item(st.session_state.user_name, selected_item, item_value)

                    # Обновляем баланс
                    new_balance = st.session_state.balance - 25
                    st.session_state.balance = new_balance
                    update_user_balance(st.session_state.user_name, new_balance)  # Обновляем баланс в базе данных

                st.session_state.spin_button_clicked = False  # Сбрасываем состояние кнопки после выполнения
            else:
                if st.button("Крутить!"):
                    st.session_state.spin_button_clicked = True  # Устанавливаем состояние кнопки при нажатии
        else:
            st.error("Недостаточно средств для крутки. Вам нужно минимум 25 рублей на балансе.")
    else:
        st.error("Пожалуйста, войдите, чтобы играть.")

# Страница профиля
elif page == "Профиль":
    st.title("Профиль")
    
    if 'user_name' in st.session_state:
        st.write(f"Добро пожаловать в ваш профиль, {st.session_state.user_name}!")
        st.write(f"Ваш баланс: {st.session_state.balance} звёзд.")
        
        items_list = get_user_items(st.session_state.user_name)
        
        if items_list:
            st.subheader("Выбитые предметы:")
            for item_name, item_value in items_list:
                if item_value==0 or  item_value==5 or item_value==15:
                    st.write(f" {item_value} звёзд")
                    st.image(item_name, width=100)  
                elif item_value==1:
                    st.write(f"подписка на пробив: {item_value} день")
                    st.image(item_name, width=100) 
                else:
                    st.write(f"подписка на пробив: {item_value} дней")
                    st.image(item_name, width=100)   
        else:
            st.write("Вы пока ничего не выбили.")
    else:
        st.error("Пожалуйста, войдите, чтобы просмотреть свой профиль.")