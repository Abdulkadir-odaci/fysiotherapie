import streamlit as st
import smtplib
from email.message import EmailMessage
import urllib.parse
import base64
import requests
from io import BytesIO
from PIL import Image
import json
import datetime

# Initialize session state variables if they don't exist
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'selected_videos' not in st.session_state:
    st.session_state.selected_videos = []
if 'video_settings' not in st.session_state:
    st.session_state.video_settings = {}
if 'client_progress' not in st.session_state:
    st.session_state.client_progress = {}


# Set the hardcoded credentials
VALID_USERNAME = "abdlkdrdci@gmail.com"
VALID_PASSWORD = "12345"

# Simple authentication function
def authenticate(username, password):
    return username == VALID_USERNAME and password == VALID_PASSWORD

# Logout function
def logout():
    st.session_state.authenticated = False
    st.session_state.selected_videos = []
    st.session_state.video_settings = {}

# Email sending function
def send_exercise_email(recipient_email, video_info, NETLIFY_BASE_URL, SENDER_EMAIL, SENDER_PASSWORD):
    """Function to send email with exercise details"""
    if st.session_state.selected_videos and recipient_email:
        # Generate a unique ID for this prescription
        prescription_id = f"rx_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create URL with selected videos and their settings
        video_params = []
        for video_id in st.session_state.selected_videos:
            sets = st.session_state.video_settings[video_id]["sets"]
            reps = st.session_state.video_settings[video_id]["reps"]
            video_params.append(f"{video_id}:{sets}:{reps}")
        
        video_query = "&videos=".join([urllib.parse.quote(param) for param in video_params])
        watch_page_url = f"{NETLIFY_BASE_URL}/watch.html?prescription={prescription_id}&videos={video_query}"
        
        # Create a list of selected videos with their set/rep details
        selected_videos_info = []
        for video_id in st.session_state.selected_videos:
            sets = st.session_state.video_settings[video_id]["sets"]
            reps = st.session_state.video_settings[video_id]["reps"]
            selected_videos_info.append(f"{video_info[video_id]['title']} ({sets} set, {reps} tekrar)")
        
        # HTML Email Content with Button and selected videos information
        email_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                <h2 style="color: #4CAF50; text-align: center;">Egzersiz Programınız</h2>
                <p>Merhaba,</p>
                <p>Size özel hazırlanmış egzersiz programınız aşağıdadır. Lütfen önerilen set ve tekrar sayılarına uygun olarak egzersizleri yapınız.</p>
                
                <h3>Seçilen Egzersizler:</h3>
                <ul style="background-color: #f9f9f9; padding: 15px; border-radius: 5px;">
                    {"".join(f"<li><strong>{info}</strong></li>" for info in selected_videos_info)}
                </ul>
                
                <div style="text-align: center; margin: 25px 0;">
                    <a href="{watch_page_url}" style="
                        display: inline-block;
                        padding: 12px 24px;
                        font-size: 16px;
                        color: white;
                        background-color: #4CAF50;
                        text-decoration: none;
                        border-radius: 5px;
                        font-weight: bold;
                    ">Egzersizleri Görüntüle</a>
                </div>
                
                <p>Her egzersiz sonrası ilerlemenizi kaydedebilirsiniz. Bu sayede terapistiniz gelişiminizi takip edebilecek.</p>
                <p>İyi egzersizler dileriz!</p>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #777;">
                    <p>Eğer buton çalışmazsa, aşağıdaki linki kullanabilirsiniz:</p>
                    <p><a href="{watch_page_url}">{watch_page_url}</a></p>
                </div>
            </div>
        </body>
        </html>
        """

        # Email Message
        msg = EmailMessage()
        msg["Subject"] = "Özel Egzersiz Programınız"
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email
        msg.set_content("Egzersiz programınızı görüntülemek için tıklayınız.")  # Fallback text
        msg.add_alternative(email_content, subtype="html")  # HTML email content

        # Send email via Gmail SMTP Server
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
                smtp.send_message(msg)

            # Save this prescription to client progress if email exists in tracking
            if recipient_email in st.session_state.client_progress:
                for video_id in st.session_state.selected_videos:
                    if video_id not in st.session_state.client_progress[recipient_email]:
                        st.session_state.client_progress[recipient_email][video_id] = {
                            "assigned_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                            "assigned_sets": st.session_state.video_settings[video_id]["sets"],
                            "assigned_reps": st.session_state.video_settings[video_id]["reps"],
                            "completed_days": [],
                            "notes": ""
                        }

            st.success(f"E-posta başarıyla {recipient_email} adresine gönderildi!")
        except Exception as e:
            st.error(f"E-posta gönderme hatası: {e}")
    else:
        st.warning("Lütfen en az bir video seçin ve alıcı e-posta adresini girin.")

# Email app
def email_app():
    st.title("🏋️ fysiotherapie")

    # Google SMTP login information
    SENDER_EMAIL = "abdulkadirodaci@gmail.com"
    SENDER_PASSWORD = "tufw gnii evqu mftt"  # Google App Password

    # Base URL for your Netlify site 
    NETLIFY_BASE_URL = "https://kaleidoscopic-semifreddo-18de16.netlify.app"

    # Complete video information with all preview videos
    video_info = {
        "bacak_egzersizi": {"title": "Bacak Egzersizi", "preview_url": f"{NETLIFY_BASE_URL}/bacak_egzersizi_preview.mp4"},
        "bacak_germe": {"title": "Bacak Germe", "preview_url": f"{NETLIFY_BASE_URL}/bacak_germe_preview.mp4"},
        "bel_egzersizi": {"title": "Bel Egzersizi", "preview_url": f"{NETLIFY_BASE_URL}/bel_egzersizi_preview.mp4"},
        "boyun_germe": {"title": "Boyun Germe", "preview_url": f"{NETLIFY_BASE_URL}/boyun_germe_preview.mp4"},
        "circle_egzersiz": {"title": "Circle Egzersizi", "preview_url": f"{NETLIFY_BASE_URL}/circle_egzersiz_preview.mp4"},
        "karin_germe": {"title": "Karın Germe", "preview_url": f"{NETLIFY_BASE_URL}/karin_germe_preview.mp4"},
        "kurbaga": {"title": "Kurbağa", "preview_url": f"{NETLIFY_BASE_URL}/kurbaga_preview.mp4"},
        "omuz_egzersizi": {"title": "Omuz Egzersizi", "preview_url": f"{NETLIFY_BASE_URL}/omuz_egzersizi_preview.mp4"},
        "squat": {"title": "Squat", "preview_url": f"{NETLIFY_BASE_URL}/squat_preview.mp4"},
        "supermen_germe": {"title": "Supermen Germe", "preview_url": f"{NETLIFY_BASE_URL}/supermen_germe_preview.mp4"},
        "ust_germe": {"title": "Üst Germe", "preview_url": f"{NETLIFY_BASE_URL}/ust_germe_preview.mp4"}
    }

    # Create tabs for application sections (only two tabs now)
    tabs = st.tabs(["Video Seçimi", "Hasta Takibi"])
    
    with tabs[0]:  # Video Selection Tab
        st.subheader("Egzersiz Videoları")
        
        # Group videos by category for easier navigation
        categories = {
            "Bacak Egzersizleri": ["bacak_egzersizi", "bacak_germe", "squat"],
            "Bel ve Karın Egzersizleri": ["bel_egzersizi", "karin_germe", "supermen_germe"],
            "Üst Vücut Egzersizleri": ["boyun_germe", "omuz_egzersizi", "ust_germe"],
            "Diğer Egzersizler": ["circle_egzersiz", "kurbaga"]
        }
        
        # Create expanders for each category
        for category, video_ids in categories.items():
            with st.expander(f"{category} ({len(video_ids)})"):
                # Create a container and 2 columns for videos in this category
                with st.container():
                    cols = st.columns(2)
                    
                    for i, video_id in enumerate(video_ids):
                        info = video_info[video_id]
                        with cols[i % 2]:
                            # Card-like container with custom styling
                            with st.container():
                                st.markdown("""
                                <style>
                                .video-container {
                                    border: 1px solid #ddd;
                                    border-radius: 5px;
                                    padding: 10px;
                                    margin-bottom: 15px;
                                }
                                </style>
                                <div class="video-container">
                                """, unsafe_allow_html=True)
                                
                                # Video title
                                st.markdown(f"<h4 style='text-align: center;'>{info['title']}</h4>", unsafe_allow_html=True)
                                
                                # Video preview
                                st.markdown(f"""
                                <div style="display: flex; justify-content: center;">
                                    <video width="160" height="120" controls>
                                        <source src="{info['preview_url']}" type="video/mp4">
                                        Your browser does not support the video tag.
                                    </video>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Selection checkbox
                                is_selected = video_id in st.session_state.selected_videos
                                if st.checkbox("Seç", value=is_selected, key=f"video_{video_id}"):
                                    if video_id not in st.session_state.selected_videos:
                                        st.session_state.selected_videos.append(video_id)
                                        # Initialize settings for this video if not already set
                                        if video_id not in st.session_state.video_settings:
                                            st.session_state.video_settings[video_id] = {"sets": 3, "reps": 10}
                                else:
                                    if video_id in st.session_state.selected_videos:
                                        st.session_state.selected_videos.remove(video_id)
                                
                                # Show sets and reps inputs if video is selected
                                if video_id in st.session_state.selected_videos:
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.session_state.video_settings[video_id]["sets"] = st.number_input(
                                            "Set", 
                                            min_value=1, 
                                            max_value=10, 
                                            value=st.session_state.video_settings[video_id]["sets"],
                                            key=f"sets_{video_id}"
                                        )
                                    with col2:
                                        st.session_state.video_settings[video_id]["reps"] = st.number_input(
                                            "Tekrar", 
                                            min_value=1, 
                                            max_value=50, 
                                            value=st.session_state.video_settings[video_id]["reps"],
                                            key=f"reps_{video_id}"
                                        )
                                
                                st.markdown("</div>", unsafe_allow_html=True)
        
        # Email sending section added at the end of the first tab
        st.markdown("---")
        st.subheader("Videoları Gönder")
        recipient_email = st.text_input("Alıcı E-posta Adresi", key="email_send")
        if st.button("Videoları Gönder", key="send_button"):
            send_exercise_email(recipient_email, video_info, NETLIFY_BASE_URL, SENDER_EMAIL, SENDER_PASSWORD)
    
    with tabs[1]:  # Patient Tracking Tab
        st.subheader("Hasta İlerleme Takibi")
        
        # Client email for tracking
        client_email = st.text_input("Hasta E-posta Adresi")
        
        if client_email:
            # Initialize client progress if not exists
            if client_email not in st.session_state.client_progress:
                st.session_state.client_progress[client_email] = {}
            
            # Display existing progress or create new entries
            if st.session_state.selected_videos:
                st.write("**Atanan Egzersizler ve İlerleme:**")
                
                for video_id in st.session_state.selected_videos:
                    # Initialize progress data for this video if not exists
                    if video_id not in st.session_state.client_progress[client_email]:
                        st.session_state.client_progress[client_email][video_id] = {
                            "assigned_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                            "assigned_sets": st.session_state.video_settings[video_id]["sets"],
                            "assigned_reps": st.session_state.video_settings[video_id]["reps"],
                            "completed_days": [],
                            "notes": ""
                        }
                    
                    # Display progress tracking for this video
                    with st.expander(f"{video_info[video_id]['title']}"):
                        progress_data = st.session_state.client_progress[client_email][video_id]
                        
                        st.write(f"**Atama Tarihi:** {progress_data['assigned_date']}")
                        st.write(f"**İstenen Set:** {progress_data['assigned_sets']}")
                        st.write(f"**İstenen Tekrar:** {progress_data['assigned_reps']}")
                        
                        completion_dates = progress_data["completed_days"]
                        if completion_dates:
                            st.write(f"**Tamamlanan Günler:** {', '.join(completion_dates)}")
                        else:
                            st.write("**Tamamlanan Gün Yok**")
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            completion_date = st.date_input(
                                "Tamamlama Tarihi", 
                                datetime.datetime.now(),
                                key=f"completion_{client_email}_{video_id}"
                            ).strftime("%Y-%m-%d")
                        with col2:
                            if st.button("Tamamlandı", key=f"complete_{client_email}_{video_id}"):
                                if completion_date not in completion_dates:
                                    completion_dates.append(completion_date)
                                    st.success(f"{completion_date} tarihinde tamamlandı olarak kaydedildi!")
                                    st.rerun()
                        
                        progress_data["notes"] = st.text_area(
                            "Notlar", 
                            value=progress_data["notes"],
                            key=f"notes_{client_email}_{video_id}"
                        )
                
                if st.button("İlerleme Raporunu İndir"):
                    progress_json = json.dumps(st.session_state.client_progress[client_email], indent=4)
                    st.download_button(
                        label="JSON İndir",
                        data=progress_json,
                        file_name=f"patient_progress_{client_email.split('@')[0]}_{datetime.datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json"
                    )
            else:
                st.warning("Önce egzersiz seçimi yapınız.")
        else:
            st.info("Hasta takibi için e-posta adresi giriniz.")
    
    # Logout button at the bottom of the app
    if st.button("Çıkış Yap", key="main_logout"):
        logout()
        st.rerun()

# Main app
def main():
    st.set_page_config(
        page_title="Fizyoterapi Egzersiz Videoları",
        page_icon="🏋️",
        layout="wide"
    )
    
    st.markdown("""
    <style>
    .stVideo {
        width: 100% !important;
        max-height: 150px !important;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    div[data-testid="stNumberInput"] {
        margin-bottom: 10px;
    }
    div[data-testid="stNumberInput"] label {
        font-weight: bold;
    }
    div[data-testid="stNumberInput"] input {
        text-align: center;
    }
    div.stNumberInput div {
        flex-direction: column;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f0f0;
        border-radius: 4px 4px 0 0;
        padding: 10px 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("🏋️ Fizyoterapi Giriş")
            with st.container():
                st.markdown("---")
                username = st.text_input("Kullanıcı Adı")
                password = st.text_input("Şifre", type="password")
                
                if st.button("Giriş Yap", use_container_width=True):
                    if authenticate(username, password):
                        st.session_state.authenticated = True
                        st.success("Giriş başarılı!")
                        st.rerun()
                    else:
                        st.error("Geçersiz kullanıcı adı veya şifre.")
    else:
        email_app()

# # HTML for the watch page
def create_watch_page_html():
    return """
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Fizyoterapi Egzersiz Videoları</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #4CAF50;
                    text-align: center;
                }
                .video-container {
                    margin-bottom: 30px;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    background-color: #f9f9f9;
                }
                .video-title {
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .video-info {
                    margin-bottom: 10px;
                    font-size: 16px;
                }
                .video-player {
                    width: 100%;
                    max-height: 400px;
                }
                .progress-tracker {
                    margin-top: 10px;
                    padding: 10px;
                    background-color: #e8f5e9;
                    border-radius: 5px;
                }
                .progress-btn {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-weight: bold;
                }
                .progress-btn:hover {
                    background-color: #45a049;
                }
                .completed {
                    background-color: #8bc34a;
                }
                .error-message {
                    color: red;
                    font-weight: bold;
                    margin: 10px 0;
                }
                .debug-info {
                    background-color: #f0f0f0;
                    padding: 10px;
                    margin: 10px 0;
                    border-radius: 5px;
                    font-family: monospace;
                    font-size: 12px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Fizyoterapi Egzersiz Programınız</h1>
                
                <!-- Test Video - Uncomment to test direct video loading -->
                <!-- 
                <div class="video-container">
                    <div class="video-title">Test Video</div>
                    <video controls class="video-player">
                        <source src="https://kaleidoscopic-semifreddo-18de16.netlify.app/bacak_egzersizi.mp4" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>
                -->
                
                <div id="video-list"></div>
                <div id="debug-info" class="debug-info" style="display: none;"></div>
            </div>

            <script>
                function addDebugInfo(message) {
                    const debugDiv = document.getElementById('debug-info');
                    debugDiv.style.display = 'block';
                    debugDiv.innerHTML += message + '<br>';
                    console.log(message);
                }

                document.addEventListener('DOMContentLoaded', function() {
                    // Video base URL - make sure this is correct
                    const baseUrl = "https://kaleidoscopic-semifreddo-18de16.netlify.app";
                    addDebugInfo("Base URL: " + baseUrl);
                    
                    // Parse URL parameters
                    const urlParams = new URLSearchParams(window.location.search);
                    const prescriptionId = urlParams.get('prescription');
                    const videosParam = urlParams.get('videos');
                    
                    addDebugInfo("Prescription ID: " + prescriptionId);
                    addDebugInfo("Videos parameter: " + videosParam);
                    
                    // Parse videos parameter
                    const videoList = document.getElementById('video-list');
                    
                    if (videosParam) {
                        const videos = videosParam.split('&videos=');
                        addDebugInfo("Parsed videos: " + JSON.stringify(videos));
                        
                        videos.forEach((videoParam, index) => {
                            addDebugInfo(`Processing video #${index+1}: ${videoParam}`);
                            
                            const [videoId, sets, reps] = decodeURIComponent(videoParam).split(':');
                            addDebugInfo(`Video ID: ${videoId}, Sets: ${sets}, Reps: ${reps}`);
                            
                            // Create video container
                            const videoContainer = document.createElement('div');
                            videoContainer.className = 'video-container';
                            
                            // Video title
                            const videoTitle = getVideoTitle(videoId);
                            const titleElement = document.createElement('div');
                            titleElement.className = 'video-title';
                            titleElement.textContent = videoTitle;
                            videoContainer.appendChild(titleElement);
                            
                            // Video info
                            const infoElement = document.createElement('div');
                            infoElement.className = 'video-info';
                            infoElement.innerHTML = `<strong>Set:</strong> ${sets} | <strong>Tekrar:</strong> ${reps}`;
                            videoContainer.appendChild(infoElement);
                            
                            // Video player
                            const videoPlayer = document.createElement('video');
                            videoPlayer.className = 'video-player';
                            videoPlayer.controls = true;
                            videoPlayer.preload = "metadata";
                            videoPlayer.playsInline = true;
                            
                            const videoUrl = `${baseUrl}/${videoId}.mp4`;
                            addDebugInfo(`Video URL: ${videoUrl}`);
                            
                            const videoSource = document.createElement('source');
                            videoSource.src = videoUrl;
                            videoSource.type = 'video/mp4';
                            
                            // Add error handling for video loading
                            videoPlayer.onerror = function() {
                                const errorCode = videoPlayer.error ? videoPlayer.error.code : "unknown";
                                addDebugInfo(`Error loading video ${videoId}: Code ${errorCode}`);
                                
                                const errorElement = document.createElement('div');
                                errorElement.className = 'error-message';
                                errorElement.textContent = `Video yüklenirken hata oluştu (Kod: ${errorCode})`;
                                videoContainer.insertBefore(errorElement, videoPlayer.nextSibling);
                            };
                            
                            videoPlayer.onloadeddata = function() {
                                addDebugInfo(`Video loaded successfully: ${videoId}`);
                            };
                            
                            videoPlayer.appendChild(videoSource);
                            videoContainer.appendChild(videoPlayer);
                            
                            // Progress tracker
                            const progressTracker = document.createElement('div');
                            progressTracker.className = 'progress-tracker';
                            
                            const progressKey = `${prescriptionId}_${videoId}`;
                            const isCompleted = localStorage.getItem(progressKey) === 'completed';
                            
                            const progressButton = document.createElement('button');
                            progressButton.className = `progress-btn ${isCompleted ? 'completed' : ''}`;
                            progressButton.textContent = isCompleted ? 'Tamamlandı ✓' : 'Tamamlandı olarak işaretle';
                            
                            progressButton.addEventListener('click', function() {
                                localStorage.setItem(progressKey, 'completed');
                                progressButton.textContent = 'Tamamlandı ✓';
                                progressButton.classList.add('completed');
                                addDebugInfo(`Marked as completed: ${videoId}`);
                            });
                            
                            progressTracker.appendChild(progressButton);
                            videoContainer.appendChild(progressTracker);
                            
                            // Add to video list
                            videoList.appendChild(videoContainer);
                        });
                        
                        // Add a button to toggle debug info
                        const toggleDebugBtn = document.createElement('button');
                        toggleDebugBtn.textContent = "Hata Ayıklama Bilgilerini Göster/Gizle";
                        toggleDebugBtn.style.marginTop = "20px";
                        toggleDebugBtn.onclick = function() {
                            const debugDiv = document.getElementById('debug-info');
                            debugDiv.style.display = debugDiv.style.display === 'none' ? 'block' : 'none';
                        };
                        document.querySelector('.container').appendChild(toggleDebugBtn);
                        
                    } else {
                        videoList.innerHTML = '<p>Videolar bulunamadı.</p>';
                        addDebugInfo("No videos parameter found in URL");
                    }
                });
                
                // Helper function to get video title from ID
                function getVideoTitle(videoId) {
                    const titles = {
                        'bacak_egzersizi': 'Bacak Egzersizi',
                        'bacak_germe': 'Bacak Germe',
                        'bel_egzersizi': 'Bel Egzersizi',
                        'boyun_germe': 'Boyun Germe',
                        'circle_egzersiz': 'Circle Egzersizi',
                        'karin_germe': 'Karın Germe',
                        'kurbaga': 'Kurbağa',
                        'omuz_egzersizi': 'Omuz Egzersizi',
                        'squat': 'Squat',
                        'supermen_germe': 'Supermen Germe',
                        'ust_germe': 'Üst Germe'
                    };
                    
                    return titles[videoId] || videoId;
                }
            </script>
        </body>
        </html>
    """
create_watch_page_html()

if __name__ == "__main__":
    main()