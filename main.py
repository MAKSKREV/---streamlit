import streamlit as st
import random
import time
import sqlite3
import hashlib

# Создание или подключение к базе данных
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Создание таблицы пользователей, если она не существует
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
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

# Функция для хеширования пароля
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Функция для регистрации пользователя
def register_user(name, password):
    initial_balance = 50  # Начальный баланс
    hashed_password = hash_password(password)
    try:
        c.execute("INSERT INTO users (name, password, balance) VALUES (?, ?, ?)", (name, hashed_password, initial_balance))
        conn.commit()
    except sqlite3.IntegrityError:
        st.error("Пользователь с таким именем уже существует.")

# Функция для получения баланса пользователя
def get_user_balance(name):
    c.execute("SELECT balance FROM users WHERE name=?", (name,))
    result = c.fetchone()
    return result[0] if result else None

# Функция для проверки пароля пользователя
def check_password(name, password):
    hashed_password = hash_password(password)
    c.execute("SELECT * FROM users WHERE name=? AND password=?", (name, hashed_password))
    return c.fetchone() is not None

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
    'image3.webp': (1, 0.1),   # 10% шанс
    'image4.webp': (7, 0.05),  # 5% шанс
    'image5.webp': (30, 0.05)   # 5% шанс
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
    password = st.text_input("Введите пароль:", type="password")

    if st.button("Зарегистрироваться"):
        if name and password:
            register_user(name, password)
            st.success(f"Пользователь {name} зарегистрирован с начальным балансом 50!")
        else:
            st.error("Пожалуйста, заполните все поля.")

# Страница входа
elif page == "Вход":
    st.title("Вход")
    user_name = st.text_input("Введите ваше имя для входа:")
    password = st.text_input("Введите пароль:", type="password")

    if st.button("Войти"):
        if check_password(user_name, password):
            balance = get_user_balance(user_name)
            st.session_state.user_name = user_name  # Сохраняем имя пользователя в session_state
            st.session_state.balance = balance  # Сохраняем баланс в session_state
            st.success(f"Добро пожаловать, {user_name}! Ваш баланс: {balance}")
        else:
            st.error("Неверное имя пользователя или пароль.")

# Страница крутилки
elif page == "Крутилка":
    if 'user_name' in st.session_state:
        st.title("Крутилка")
        st.write(f"Ваш баланс: {st.session_state.balance}")

        if st.button("Крутить"):
            selected_item = spin_items()
            item_value = items_with_chances[selected_item][0]
            new_balance = st.session_state.balance + item_value
            update_user_balance(st.session_state.user_name, new_balance)
            save_item(st.session_state.user_name, selected_item, item_value)
            st.session_state.balance = new_balance
            st.success(f"Вы выбили {selected_item} на сумму {item_value}. Ваш новый баланс: {new_balance}")
    else:
        st.error("Пожалуйста, войдите, чтобы использовать крутилку.")

# Страница профиля
elif page == "Профиль":
    if 'user_name' in st.session_state:
        st.title("Профиль")
        st.write(f"Имя пользователя: {st.session_state.user_name}")
        st.write(f"Баланс: {st.session_state.balance}")
        
        items = get_user_items(st.session_state.user_name)
        if items:
            st.write("Ваши выбитые предметы:")
            for item_name, item_value in items:
                st.write(f"{item_name} - {item_value}")
        else:
            st.write("У вас пока нет выбитых предметов.")
    else:
        st.error("Пожалуйста, войдите, чтобы просмотреть профиль.")

# Закрытие соединения с базой данных
conn.close()