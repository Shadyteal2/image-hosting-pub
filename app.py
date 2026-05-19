import streamlit as st
import os
import concurrent.futures
import time
import io
import requests
import base64
from PIL import Image, ExifTags
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


# --- Configuration ---
st.set_page_config(
    page_title="ImageSync Public | Global Image Hosting",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State Keys
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# --- Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --bg-dark: #050507;
        --surface-dark: rgba(13, 13, 17, 0.7);
        --accent: linear-gradient(135deg, #A855F7 0%, #6366F1 50%, #06B6D4 100%);
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --border-color: rgba(255, 255, 255, 0.06);
    }

    .stApp {
        background-color: var(--bg-dark);
        color: var(--text-primary);
        font-family: 'Outfit', sans-serif;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(6, 6, 8, 0.95) !important;
        border-right: 1px solid var(--border-color);
        backdrop-filter: blur(30px);
    }
    
    [data-testid="stSidebar"] h3 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }

    /* Text Inputs */
    .stTextInput input {
        background-color: rgba(10, 10, 14, 0.8) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        font-family: 'Outfit', sans-serif !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stTextInput input:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.2) !important;
        background-color: rgba(15, 15, 22, 0.9) !important;
    }

    /* Custom Uploader Glow */
    [data-testid="stFileUploader"] {
        background: rgba(10, 10, 14, 0.4) !important;
        border: 1px dashed rgba(99, 102, 241, 0.3) !important;
        border-radius: 24px !important;
        padding: 2.5rem !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #A855F7 !important;
        background: rgba(15, 15, 22, 0.6) !important;
        box-shadow: 0 0 35px rgba(168, 85, 247, 0.15) !important;
        transform: translateY(-2px);
    }

    /* Streamlit Containers / Cards */
    [data-testid="stElementContainer"] div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px !important;
        border: 1px solid var(--border-color) !important;
        background-color: var(--surface-dark) !important;
        backdrop-filter: blur(20px) !important;
        padding: 1.5rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    [data-testid="stElementContainer"] div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(99, 102, 241, 0.3) !important;
        box-shadow: 0 10px 40px rgba(99, 102, 241, 0.08) !important;
    }

    .main-header {
        font-size: 3.8rem;
        font-weight: 800;
        background: var(--accent);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
        letter-spacing: -2.5px;
        display: flex;
        align-items: center;
        gap: 20px;
        font-family: 'Outfit', sans-serif;
    }

    .main-header span {
        -webkit-text-fill-color: var(--text-secondary);
        font-size: 1.35rem;
        font-weight: 500;
        letter-spacing: -0.5px;
        background: none;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: var(--text-secondary);
        margin-bottom: 3.5rem;
        font-weight: 400;
        letter-spacing: -0.2px;
    }

    /* Primary buttons */
    .stButton>button {
        background: var(--accent) !important;
        color: white !important;
        border: none !important;
        padding: 0.9rem 1.8rem !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100% !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: none !important;
        letter-spacing: 0.2px !important;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.25) !important;
        font-family: 'Outfit', sans-serif !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(168, 85, 247, 0.4) !important;
    }
    
    /* Sliders and Dividers */
    hr {
        border-color: var(--border-color) !important;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
    }
    ::-webkit-scrollbar-thumb {
        background: #232329;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #363640;
    }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 6rem 2rem;
        background: rgba(13, 13, 17, 0.4);
        border-radius: 32px;
        border: 1px dashed var(--border-color);
        margin: 2.5rem 0;
        backdrop-filter: blur(20px);
        transition: border-color 0.3s ease;
    }
    .empty-state:hover {
        border-color: rgba(99, 102, 241, 0.3);
    }

    .empty-state h3 {
        background: var(--accent);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }

    .live-preview-link {
        color: #06B6D4;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.9rem;
        margin-top: 12px;
        padding: 10px;
        border-radius: 10px;
        background: rgba(6, 182, 212, 0.05);
        border: 1px solid rgba(6, 182, 212, 0.1);
        transition: all 0.3s ease;
    }
    
    .live-preview-link:hover {
        background: rgba(6, 182, 212, 0.1);
        border-color: rgba(6, 182, 212, 0.3);
        transform: translateX(2px);
    }

    /* Skeleton Loading effect */
    .skeleton {
        background: linear-gradient(90deg, rgba(13, 13, 17, 0.6) 25%, rgba(28, 28, 36, 0.8) 50%, rgba(13, 13, 17, 0.6) 75%);
        background-size: 200% 100%;
        animation: loading 1.4s infinite cubic-bezier(0.4, 0, 0.2, 1);
        border-radius: 12px;
    }

    @keyframes loading {
        0% {
            background-position: 200% 0;
        }
        100% {
            background-position: -200% 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Logic Functions ---

def create_robust_session():
    """Create a requests.Session with connection pooling, Keep-Alive, and retry policies."""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "POST", "PATCH", "PUT"]
    )
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=32,
        pool_maxsize=32
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def optimize_image(uploaded_file, name, quality=80):
    """Process image: fix auto-orientation, limit size (QHD 2560px), convert to WebP, and return bytes."""
    try:
        img = Image.open(uploaded_file)
        
        # High-Fidelity Auto-Orientation based on EXIF tag 274
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = img._getexif()
            if exif is not None:
                val = exif.get(orientation)
                if val == 3:
                    img = img.rotate(180, expand=True)
                elif val == 6:
                    img = img.rotate(270, expand=True)
                elif val == 8:
                    img = img.rotate(90, expand=True)
        except Exception:
            pass # Safe fallback for missing/corrupted metadata
            
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGBA")
        else:
            img = img.convert("RGB")
            
        # Max resolution ceiling for optimal web hosting performance (QHD 2560px)
        max_dim = 2560
        if max(img.size) > max_dim:
            img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
            
        buf = io.BytesIO()
        img.save(buf, "WEBP", quality=quality, method=4)
        return {"name": name, "content": buf.getvalue(), "success": True}
    except Exception as e:
        return {"name": name, "error": str(e), "success": False}

def create_github_blob(session, token, repo, content_bytes):
    """Create a git blob on GitHub using connection pooling and return its SHA."""
    url = f"https://api.github.com/repos/{repo}/git/blobs"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    content_b64 = base64.b64encode(content_bytes).decode('utf-8')
    data = {
        "content": content_b64,
        "encoding": "base64"
    }
    try:
        res = session.post(url, headers=headers, json=data, timeout=30)
        if res.status_code == 201:
            return {"success": True, "sha": res.json()["sha"]}
        else:
            return {"success": False, "error": res.json().get('message', 'Unknown error')}
    except Exception as e:
        return {"success": False, "error": str(e)}

def upload_batch_to_github(token, repo, branch, folder, file_infos, commit_message, progress_callback=None):
    """Upload a batch of files in a single commit using pooled connections and concurrent workers."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        session = create_robust_session()
        
        # 1. Get the latest commit SHA of the branch reference
        ref_url = f"https://api.github.com/repos/{repo}/git/ref/heads/{branch}"
        ref_res = session.get(ref_url, headers=headers, timeout=20)
        if ref_res.status_code != 200:
            return {"success": False, "error": f"Failed to get branch reference: {ref_res.json().get('message', 'Unknown error')}"}
        
        commit_sha = ref_res.json()["object"]["sha"]
        
        # 2. Get the base tree SHA of that commit
        commit_url = f"https://api.github.com/repos/{repo}/git/commits/{commit_sha}"
        commit_res = session.get(commit_url, headers=headers, timeout=20)
        if commit_res.status_code != 200:
            return {"success": False, "error": f"Failed to get base commit: {commit_res.json().get('message', 'Unknown error')}"}
            
        base_tree_sha = commit_res.json()["tree"]["sha"]
        
        # 3. Upload all files as blobs in parallel using custom sized concurrent workers
        max_workers = max(4, min(len(file_infos), 16))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(create_github_blob, session, token, repo, img["content"]): img for img in file_infos}
            
            tree_nodes = []
            errors = []
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                img = futures[future]
                res = future.result()
                if res["success"]:
                    path = f"{folder}/{img['name']}"
                    tree_nodes.append({
                        "path": path,
                        "mode": "100644",
                        "type": "blob",
                        "sha": res["sha"]
                    })
                else:
                    errors.append(f"Blob failed for {img['name']}: {res['error']}")
                
                if progress_callback:
                    progress_callback(i + 1, len(file_infos), img["name"])
                    
        if errors:
            return {"success": False, "error": "; ".join(errors)}
            
        # 4. Create a new tree with base_tree pointing to existing files
        tree_url = f"https://api.github.com/repos/{repo}/git/trees"
        tree_data = {
            "base_tree": base_tree_sha,
            "tree": tree_nodes
        }
        tree_res = session.post(tree_url, headers=headers, json=tree_data, timeout=30)
        if tree_res.status_code != 201:
            return {"success": False, "error": f"Failed to create new tree: {tree_res.json().get('message', 'Unknown error')}"}
            
        new_tree_sha = tree_res.json()["sha"]
        
        # 5. Create a new commit pointing to the new tree and the parent commit
        commit_post_url = f"https://api.github.com/repos/{repo}/git/commits"
        commit_data = {
            "message": commit_message,
            "tree": new_tree_sha,
            "parents": [commit_sha]
        }
        commit_post_res = session.post(commit_post_url, headers=headers, json=commit_data, timeout=30)
        if commit_post_res.status_code != 201:
            return {"success": False, "error": f"Failed to create commit: {commit_post_res.json().get('message', 'Unknown error')}"}
            
        new_commit_sha = commit_post_res.json()["sha"]
        
        # 6. Update the branch reference to point to the new commit
        ref_update_url = f"https://api.github.com/repos/{repo}/git/refs/heads/{branch}"
        ref_update_data = {
            "sha": new_commit_sha,
            "force": False
        }
        ref_update_res = session.patch(ref_update_url, headers=headers, json=ref_update_data, timeout=30)
        if ref_update_res.status_code != 200:
            return {"success": False, "error": f"Failed to update reference: {ref_update_res.json().get('message', 'Unknown error')}"}
            
        # Construct success uploads in standard format
        raw_urls = []
        for img in file_infos:
            raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{folder}/{img['name']}"
            raw_urls.append({"name": img['name'], "url": raw_url, "success": True})
            
        return {"success": True, "uploads": raw_urls}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# --- Sidebar Configuration ---

with st.sidebar:
    st.markdown("### 🛠️ Configuration")
    gh_token = st.text_input("GitHub PAT", type="password", help="Personal Access Token with 'repo' scope.")
    gh_repo = st.text_input("Repository Path", placeholder="username/repo-name", help="Format: owner/repo")
    gh_branch = st.text_input("Target Branch", value="main")
    gh_folder = st.text_input("Target Folder", value="assets")
    
    if gh_repo and gh_branch and gh_folder:
        folder_url = f"https://github.com/{gh_repo}/tree/{gh_branch}/{gh_folder}"
        st.markdown(f"""
            <a href="{folder_url}" target="_blank" class="live-preview-link">
                📁 View Repository Folder ↗
            </a>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 🏷️ Bulk Renaming")
    base_name = st.text_input("Base Filename", placeholder="e.g. project-assets", help="Files will be named base-1.webp, base-2.webp, etc.")
    
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
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}"
)

if uploaded_files:
    if not (gh_token and gh_repo):
        st.warning("⚠️ Please provide your GitHub Token and Repository Path in the sidebar to proceed.")
    else:
        # Action Buttons Summary Card
        with st.container(border=True):
            st.markdown(f"📊 **Selected {len(uploaded_files)} files for optimization**")
            
            # File list preview
            with st.expander(f"📁 Selected Files List ({len(uploaded_files)})", expanded=True):
                for f in uploaded_files:
                    st.markdown(f"- `{f.name}` ({(f.size / 1024):.1f} KB)")
            
            col_clear, col_deploy = st.columns([1, 2])
            with col_clear:
                if st.button("🧹 Clear All Files", use_container_width=True):
                    st.session_state.uploader_key += 1
                    st.rerun()
            with col_deploy:
                deploy_btn = st.button("🚀 Process & Deploy", use_container_width=True)
        
        if deploy_btn:
            progress_bar = st.progress(0)
            status = st.empty()
            
            # Show a beautiful pulsing skeleton loader
            skeleton_placeholder = st.empty()
            skeleton_placeholder.markdown("""
                <div style="padding: 1.5rem; background: rgba(18, 18, 20, 0.7); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 2rem;">
                    <h4 style="color: #8B5CF6; margin-bottom: 1rem; font-family: 'Inter', sans-serif;">⚡ Processing and Syncing...</h4>
                    <div class="skeleton" style="height: 20px; width: 60%; margin-bottom: 12px;"></div>
                    <div class="skeleton" style="height: 15px; width: 85%; margin-bottom: 12px;"></div>
                    <div class="skeleton" style="height: 15px; width: 40%; margin-bottom: 24px;"></div>
                    <div class="skeleton" style="height: 120px; width: 100%;"></div>
                </div>
            """, unsafe_allow_html=True)
            
            # Step 1: Optimize in parallel
            status.markdown("🎨 **Step 1/2: Optimizing Images...**")
            results_process = []
            
            # Pre-calculate names to avoid collisions/complexity in threads
            processed_names = []
            for i, f in enumerate(uploaded_files):
                if base_name:
                    processed_names.append(f"{base_name}-{i+1}.webp")
                else:
                    stem = Path(f.name).stem
                    processed_names.append(f"{stem}-{i+1}.webp")
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(optimize_image, f, n, quality) for f, n in zip(uploaded_files, processed_names)]
                for i, future in enumerate(concurrent.futures.as_completed(futures)):
                    results_process.append(future.result())
                    progress_bar.progress(int(((i + 1) / len(uploaded_files)) * 50))
            
            # Step 2: Deploy to GitHub in a single commit using the Git Database API
            status.markdown("☁️ **Step 2/2: Deploying to GitHub...**")
            valid_images = [r for r in results_process if r['success']]
            
            if valid_images:
                commit_msg = f"Upload {len(valid_images)} images via ImageSync Public"
                if base_name:
                    commit_msg = f"Upload {base_name} assets ({len(valid_images)} files) via ImageSync Public"
                
                def update_progress(current, total, name):
                    status.markdown(f"☁️ **Step 2/2: Uploaded {name} ({current}/{total})...**")
                    progress_bar.progress(50 + int((current / total) * 50))
                
                res = upload_batch_to_github(
                    token=gh_token,
                    repo=gh_repo,
                    branch=gh_branch,
                    folder=gh_folder,
                    file_infos=valid_images,
                    commit_message=commit_msg,
                    progress_callback=update_progress
                )
                
                if res["success"]:
                    final_results = res["uploads"]
                else:
                    st.error(f"💥 Batch deployment failed: {res['error']}")
                    final_results = [{"name": img['name'], "error": res["error"], "success": False} for img in valid_images]
            else:
                final_results = []
            
            # Clear skeleton and loading states when done
            skeleton_placeholder.empty()
            status.empty()
            progress_bar.empty()
            
            # Display Gallery
            success_uploads = [r for r in final_results if r['success']]
            if success_uploads:
                st.success(f"✅ Successfully deployed {len(success_uploads)} images!")
                
                cols = st.columns(3)
                for idx, res in enumerate(success_uploads):
                    with cols[idx % 3]:
                        with st.container(border=True):
                            st.markdown(f"**🔗 {res['name']}**")
                            st.code(res['url'], language="text")
                            with st.expander("👁️ View Preview", expanded=False):
                                st.image(res['url'], use_container_width=True)
            
            errors = [r for r in final_results if not r['success']]
            if errors:
                with st.expander("❌ View Errors"):
                    for e in errors:
                        st.error(f"**{e['name']}**: {e.get('error', 'Upload failed')}")

else:
    # Empty state / Welcome
    st.markdown("""
    <div class="empty-state">
        <h3>Ready to optimize?</h3>
        <p style="color: var(--text-muted); max-width: 400px; margin: 0 auto;">
            Drop your images above to begin. We'll handle the conversion to <b>WebP</b> and deploy directly to your GitHub repository.
        </p>
        <div style="margin-top: 1.5rem; font-size: 0.8rem; color: #555;">
            Supports PNG, JPG, JPEG, and WebP
        </div>
    </div>
    """, unsafe_allow_html=True)
