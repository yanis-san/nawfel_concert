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

def creds_entered():
    if st.session_state["user"].strip()=="admin" and st.session_state["passwd"].strip()=="chacal":
        st.session_state["authenticated"]=True
    else:
        st.session_state["authenticated"]=False
        if not st.session_state["passwd"]:
            st.warning("Entrez un mot de passe")
        elif not st.session_state["user"]:
            st.warning("Entrez un nom d'utilisateur")
        else:
        
            st.error("invalid username password chacal")
def authenticate_user():
    if "authenticated" not in st.session_state:

        st.text_input(label="Username:",value="",key="user",on_change=creds_entered)
        st.text_input(label="Password:",value="",key="passwd",type="password",on_change=creds_entered)
        return False
    else:
        if st.session_state["authenticated"]:
            return True
        else:
            st.text_input(label="Username:",value="",key="user",on_change=creds_entered)
            st.text_input(label="Password:",value="",key="passwd",type="password",on_change=creds_entered)
            return False

if authenticate_user():
    show_database_data()
