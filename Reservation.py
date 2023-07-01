import sqlite3
import qrcode
import streamlit as st
from reportlab.pdfgen import canvas
from PIL import Image
from io import BytesIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import matplotlib.pyplot as plt
import yaml
from yaml.loader import SafeLoader
import pickle
from pathlib import Path
import streamlit_authenticator as stauth

# Créer une connexion à la base de données (création si elle n'existe pas)
conn = sqlite3.connect("concert.db")
c = conn.cursor()

# Créer la table "clients" si elle n'existe pas déjà
c.execute("""CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                phone TEXT,
                age INTEGER,
                gender TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )""")
conn.commit()

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    return qr_img

def generate_pdf(data):
    # Générer le QR code
    qr_img = generate_qr_code(data)

    # Convertir le QR code en format PNG
    buffered = BytesIO()
    qr_img.save(buffered, format="PNG")
    qr_img_data = buffered.getvalue()

    # Générer le PDF
    pdf_buffer = BytesIO()
    pdf_canvas = canvas.Canvas(pdf_buffer)

    # Insérer le QR code dans le PDF
    qr_img_stream = BytesIO(qr_img_data)
    qr_img_obj = Image.open(qr_img_stream)
    pdf_canvas.drawInlineImage(qr_img_obj, x=100, y=600, width=200, height=200)

    # Insérer l'image dans le PDF
    image_path = "test.jpg"  # Remplacez par le chemin de votre image
    image = Image.open(image_path)
    image = image.resize((200, 200))  # Redimensionnez selon vos besoins
    pdf_canvas.drawInlineImage(image, x=350, y=600, width=200, height=200)

    # Autres informations dans le PDF
    pdf_canvas.setFont("Helvetica", 12)
    pdf_canvas.drawString(100, 550, "Informations du client:")
    pdf_canvas.setFont("Helvetica", 10)
    lines = data.split("\n")
    line_height = 20
    y = 520
    for line in lines:
        pdf_canvas.drawString(100, y, line)
        y -= line_height

    # Enregistrer le contenu du PDF dans le buffer
    pdf_canvas.save()

    # Récupérer les données du PDF
    pdf_data = pdf_buffer.getvalue()

    return pdf_data

def send_email_with_pdf(pdf_data, email):
    from_addr = "yanisb598@gmail.com"  # Adresse e-mail de l'expéditeur
    password = "sygdjygofjcxboxs"  # Mot de passe de l'expéditeur

    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = email
    msg["Subject"] = "Votre e-ticket"

    # Attachement du PDF
    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(pdf_data)
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename="ticket.pdf")
    msg.attach(attachment)

    # Envoi du e-mail
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_addr, password)
    server.send_message(msg)
    server.quit()

def main():
    st.title("Recevez votre e-ticket")

    # Saisie des données du client
    name = st.text_input("Nom complet")
    email = st.text_input("Adresse e-mail")
    phone = st.text_input("Numéro de téléphone")
    age = st.number_input("Âge", min_value=0, max_value=150, step=1)
    gender = st.radio("Sexe", ("Homme", "Femme"))

    if st.button("Générer le ticket"):
        # Vérifier que les informations sont saisies
        if not name or not email or not phone:
            st.warning("Veuillez saisir toutes les informations.")
            return

        # Ajouter le client à la base de données
        c.execute("INSERT INTO clients (name, email, phone, age, gender) VALUES (?, ?, ?, ?, ?)",
                  (name, email, phone, age, gender))
        conn.commit()

        # Récupérer l'ID du client
        client_id = c.lastrowid

        # Récupérer l'heure et la date actuelles
        c.execute("SELECT timestamp FROM clients WHERE id = ?", (client_id,))
        timestamp = c.fetchone()[0]

        # Générer les données du ticket
        ticket_data = f"ID client : {client_id}\nNom : {name}\nEmail : {email}\nNuméro de téléphone : {phone}\nÂge : {age}\nSexe : {gender}\nDate et heure : {timestamp}"

        # Générer le PDF avec le QR code et l'image
        pdf_data = generate_pdf(ticket_data)

        # Envoyer le PDF par e-mail
        send_email_with_pdf(pdf_data, email)

        st.success("Votre e-ticket a été envoyé par e-mail.")

if __name__ == "__main__":
    main()
