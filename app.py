import streamlit as st
import os
import concurrent.futures
import time
import io
import requests
import base64
from PIL import Image
from pathlib import Path

# --- Configuration ---
st.set_page_config(
    page_title="ImageSync Public | Global Image Hosting",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: baseline;
        gap: 15px;
    }

    .main-header span {
        -webkit-text-fill-color: #888899;
        font-size: 1.5rem;
        font-weight: 400;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #888899;
        margin-bottom: 2rem;
    }

    .stButton>button {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(106, 17, 203, 0.5);
        color: white;
    }

    .card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1rem;
    }

    .url-box {
        background: #16213e;
        padding: 10px;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        color: #4cc9f0;
        border: 1px solid #4361ee;
        margin-top: 5px;
        word-break: break-all;
    }
</style>
""", unsafe_allow_html=True)

# --- Logic Functions ---

def optimize_image(uploaded_file, name, quality=80):
    """Process image: resize/convert to WebP and return bytes."""
    try:
        img = Image.open(uploaded_file)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGBA")
        else:
            img = img.convert("RGB")
            
        buf = io.BytesIO()
        img.save(buf, "webp", quality=quality)
        return {"name": name, "content": buf.getvalue(), "success": True}
    except Exception as e:
        return {"name": name, "error": str(e), "success": False}

def upload_to_github(token, repo, branch, folder, file_info):
    """Upload a single file to GitHub via REST API."""
    url = f"https://api.github.com/repos/{repo}/contents/{folder}/{file_info['name']}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 1. Check if file exists to get SHA (for updates)
    sha = None
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json().get('sha')
    
    # 2. Upload/Update
    content_b64 = base64.b64encode(file_info['content']).decode('utf-8')
    data = {
        "message": f"Upload {file_info['name']} via ImageSync Public",
        "content": content_b64,
        "branch": branch
    }
    if sha:
        data["sha"] = sha
        
    res = requests.put(url, headers=headers, json=data)
    if res.status_code in [200, 201]:
        raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{folder}/{file_info['name']}"
        return {"name": file_info['name'], "url": raw_url, "success": True}
    else:
        error_msg = res.json().get('message', 'Unknown error')
        return {"name": file_info['name'], "error": error_msg, "success": False}

# --- Sidebar Configuration ---

with st.sidebar:
    st.markdown("### 🛠️ Configuration")
    gh_token = st.text_input("GitHub PAT", type="password", help="Personal Access Token with 'repo' scope.")
    gh_repo = st.text_input("Repository Path", placeholder="username/repo-name", help="Format: owner/repo")
    gh_branch = st.text_input("Target Branch", value="main")
    gh_folder = st.text_input("Target Folder", value="assets")
    
    st.divider()
    st.markdown("### ⚙️ Optimization")
    quality = st.slider("WebP Quality", 10, 100, 80)
    
    st.divider()
    st.info("💡 Your token is never stored. It remains in session memory only.")

# --- Main Interface ---

st.markdown('<div class="main-header">ImageSync Public <span>by Shady</span></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Professional Image Optimization & GitHub Hosting</div>', unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Upload images (Max 200MB total)", 
    type=['png', 'jpg', 'jpeg', 'webp'], 
    accept_multiple_files=True
)

if uploaded_files:
    if not (gh_token and gh_repo):
        st.warning("⚠️ Please provide your GitHub Token and Repository Path in the sidebar to proceed.")
    else:
        if st.button("🚀 Process & Deploy"):
            progress_bar = st.progress(0)
            status = st.empty()
            
            # Step 1: Optimize in parallel
            status.markdown("🎨 **Step 1/2: Optimizing Images...**")
            results_process = []
            
            # Pre-calculate names to avoid collisions/complexity in threads
            processed_names = []
            for i, f in enumerate(uploaded_files):
                stem = Path(f.name).stem
                processed_names.append(f"{stem}-{i+1}.webp")
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(optimize_image, f, n, quality) for f, n in zip(uploaded_files, processed_names)]
                for i, future in enumerate(concurrent.futures.as_completed(futures)):
                    results_process.append(future.result())
                    progress_bar.progress(int(((i + 1) / len(uploaded_files)) * 50))
            
            # Step 2: Upload in parallel
            status.markdown("☁️ **Step 2/2: Deploying to GitHub...**")
            final_results = []
            valid_images = [r for r in results_process if r['success']]
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(upload_to_github, gh_token, gh_repo, gh_branch, gh_folder, img) for img in valid_images]
                for i, future in enumerate(concurrent.futures.as_completed(futures)):
                    final_results.append(future.result())
                    progress_bar.progress(50 + int(((i + 1) / len(valid_images)) * 50))
            
            status.empty()
            progress_bar.empty()
            
            # Display Gallery
            success_uploads = [r for r in final_results if r['success']]
            if success_uploads:
                st.success(f"✅ Successfully deployed {len(success_uploads)} images!")
                
                cols = st.columns(3)
                for idx, res in enumerate(success_uploads):
                    with cols[idx % 3]:
                        st.markdown(f'<div class="card">', unsafe_allow_html=True)
                        st.image(res['url'], caption=res['name'], use_container_width=True)
                        st.markdown(f'<b>Raw URL:</b>', unsafe_allow_html=True)
                        st.code(res['url'], language="text")
                        st.markdown('</div>', unsafe_allow_html=True)
            
            errors = [r for r in final_results if not r['success']]
            if errors:
                with st.expander("❌ View Errors"):
                    for e in errors:
                        st.error(f"**{e['name']}**: {e.get('error', 'Upload failed')}")

else:
    # Empty state / Welcome
    st.markdown("""
    <div style="text-align: center; padding: 3rem; background: rgba(255,255,255,0.03); border-radius: 20px; border: 1px dashed rgba(255,255,255,0.1);">
        <h3 style="color: #6a11cb;">Ready to start?</h3>
        <p>Drop your images above and configure your GitHub settings in the sidebar.</p>
        <p style="font-size: 0.8rem; color: #666;">Supports PNG, JPG, JPEG, and WebP formats.</p>
    </div>
    """, unsafe_allow_html=True)
