import streamlit as st
import smtplib
from email.message import EmailMessage
import urllib.parse
from dotenv import load_dotenv  # to take the email and pasw from env

# Initialize session state variables if they don't exist
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Set the hardcoded credentials
VALID_USERNAME = "abdlkdrdci@gmail.com"
VALID_PASSWORD = "12345"

# Simple authentication function
def authenticate(username, password):
    if username == VALID_USERNAME and password == VALID_PASSWORD:
        return True
    return False

# Logout function
def logout():
    st.session_state.authenticated = False

# Email sending app (your existing code)
def email_app():
    st.title("🏋️ fysiotherapie")

    # Google SMTP Giriş Bilgileri (Sabit)
    SENDER_EMAIL = "abdulkadirodaci@gmail.com"
    SENDER_PASSWORD = "tufw gnii evqu mftt"  # Google App Password kullanın

    # Alıcı e-posta adresi
    recipient_email = st.text_input("Alıcı E-posta Adresi")

    # Kullanıcının seçebileceği videolar
    video_names = [
        "bacak_egzersizi",
        "bacak_germe",
        "bel_egzersizi",
        "boyun_germe",
        "circle_egzersiz",
        "karin_germe",
        "kurbaga",
        "omuz_egzersizi",
        "squat",
        "supermen_germe",
        "ust_germe"
    ]

    # UI: Kullanıcının birden fazla video seçmesini sağla
    selected_videos = st.multiselect("Göndermek istediğiniz videoları seçin:", video_names)

    # Video bağlantıları oluştur
    if st.button("Videoları Gönder"):
        if selected_videos and recipient_email:
            # Seçili videoları URL'ye ekleyerek bağlantı oluştur
            video_query = "&videos=".join([urllib.parse.quote(video) for video in selected_videos])
            watch_page_url = f"https://kaleidoscopic-semifreddo-18de16.netlify.app/watch.html?videos={video_query}"
            # HTML Email Content with Button
            email_content = f"""
            <html>
            <body>
                <p>Butona tiklayarak sizin icin secilmis egzersiz videolarini lutfen izleyin. </p>
                <a href="{watch_page_url}" style="
                    display: inline-block;
                    padding: 10px 20px;
                    font-size: 16px;
                    color: white;
                    background-color: #007BFF;
                    text-decoration: none;
                    border-radius: 5px;
                ">Egzersiz videolari</a>
                <p>Buton calismadigi muddetce lutfen bu linkten ulasin. </p>
                <p><a href="{watch_page_url}">{watch_page_url}</a></p>
            </body>
            </html>
            """

            # Email Message
            msg = EmailMessage()
            msg["Subject"] = "egzersiz videolariniz"
            msg["From"] = SENDER_EMAIL
            msg["To"] = recipient_email
            msg.set_content("videolari izlemek icin tiklayiniz.")  # Fallback text
            msg.add_alternative(email_content, subtype="html")  # HTML email content

            # Gmail SMTP Sunucusu Üzerinden E-posta Gönderme
            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                    smtp.login(SENDER_EMAIL, SENDER_PASSWORD)  # Sabit şifre kullanılıyor
                    smtp.send_message(msg)

                st.success(f"E-posta başarıyla {recipient_email} adresine gönderildi!")
            except Exception as e:
                st.error(f"E-posta gönderme hatası: {e}")
        else:
            st.warning("Lütfen en az bir video seçin ve alıcı e-posta adresini girin.")
            
    # Add a logout button
    if st.button("Çıkış Yap"):
        logout()
        st.rerun()

# Main app
def main():
    # If not authenticated, show login page
    if not st.session_state.authenticated:
        st.title("Giriş")
        
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        
        if st.button("Giriş Yap"):
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.success("Giriş başarılı!")
                st.rerun()
            else:
                st.error("Geçersiz kullanıcı adı veya şifre.")
    
    # If authenticated, show the email app
    else:
        email_app()

if __name__ == "__main__":
    main()