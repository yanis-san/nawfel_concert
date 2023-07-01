import sqlite3
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader




# Créer une connexion à la base de données
conn = sqlite3.connect("concert.db")
c = conn.cursor()


def show_database_data():
  
    st.title("Base de données des clients")

    # Récupérer les données de la base de données
    c.execute("SELECT id, name, email, phone, age, gender, timestamp FROM clients")
    rows = c.fetchall()

    # Afficher les données dans un DataFrame
    df = pd.DataFrame(rows, columns=["ID", "Nom", "Email", "Numéro de téléphone", "Âge", "Sexe", "Date et heure"])
    st.dataframe(df)

    # Répartition des genres
    st.subheader("Répartition des genres")
    gender_counts = df["Sexe"].value_counts()
    fig, ax = plt.subplots()
    sns.barplot(x=gender_counts.index, y=gender_counts.values, ax=ax)
    plt.xlabel("Sexe")
    plt.ylabel("Nombre de clients")
    st.pyplot(fig)

    # Répartition des âges
    st.subheader("Répartition des âges")
    fig, ax = plt.subplots()
    sns.histplot(data=df, x="Âge", bins=20, kde=True, ax=ax)
    plt.xlabel("Âge")
    plt.ylabel("Nombre de clients")
    st.pyplot(fig)

    # Check authentication status


st.title("Login")
tentative_pass=st.text_input("Password",type="password")

if tentative_pass:
    if tentative_pass==st.secrets["SECRET_KEY"]:
        show_database_data()
    else:
        st.warning("Mot de passe incorrect")
    
        


