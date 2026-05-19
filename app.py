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

# Initialize Session State Keys
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# --- Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    :root {
        --bg-dark: #0A0A0B;
        --surface-dark: rgba(18, 18, 20, 0.7);
        --accent: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
        --text-muted: #888899;
        --border-color: rgba(255, 255, 255, 0.1);
    }

    .stApp {
        background-color: var(--bg-dark);
        color: #E2E8F0;
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 10, 11, 0.9) !important;
        border-right: 1px solid var(--border-color);
        backdrop-filter: blur(20px);
    }

    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: var(--accent);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
        letter-spacing: -2px;
        display: flex;
        align-items: center;
        gap: 20px;
    }

    .main-header span {
        -webkit-text-fill-color: var(--text-muted);
        font-size: 1.25rem;
        font-weight: 500;
        letter-spacing: 0;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: var(--text-muted);
        margin-bottom: 3rem;
        font-weight: 400;
    }

    /* Re-styling primary buttons */
    .stButton>button {
        background: var(--accent) !important;
        color: white !important;
        border: none !important;
        padding: 0.8rem 1.5rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: none !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.5) !important;
    }

    /* Glass Cards */
    .card {
        background: var(--surface-dark);
        backdrop-filter: blur(12px);
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid var(--border-color);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease;
    }
    
    .card:hover {
        border-color: rgba(139, 92, 246, 0.4);
    }

    .url-box {
        background: rgba(0, 0, 0, 0.3);
        padding: 12px;
        border-radius: 10px;
        font-family: 'Inter', monospace;
        font-size: 0.85rem;
        color: #60A5FA;
        border: 1px solid rgba(96, 165, 250, 0.2);
        margin-top: 10px;
        word-break: break-all;
        position: relative;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
    }
    ::-webkit-scrollbar-thumb {
        background: #2D2D30;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #3B3B3F;
    }

    /* Empty state styling */
    .empty-state {
        text-align: center;
        padding: 5rem 2rem;
        background: var(--surface-dark);
        border-radius: 30px;
        border: 1px dashed var(--border-color);
        margin: 2rem 0;
    }

    .empty-state h3 {
        color: #8B5CF6;
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }

    .copy-btn {
        background: rgba(139, 92, 246, 0.1);
        color: #A78BFA;
        border: 1px solid rgba(139, 92, 246, 0.2);
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        cursor: pointer;
        margin-top: 8px;
        display: inline-block;
        transition: all 0.2s ease;
    }

    .copy-btn:hover {
        background: rgba(139, 92, 246, 0.2);
        color: white;
    }

    .live-preview-link {
        color: #60A5FA;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.9rem;
        margin-top: 10px;
        padding: 8px;
        border-radius: 8px;
        background: rgba(96, 165, 250, 0.05);
        border: 1px solid rgba(96, 165, 250, 0.1);
    }
    
    .live-preview-link:hover {
        background: rgba(96, 165, 250, 0.1);
        border-color: rgba(96, 165, 250, 0.3);
    }

    /* Skeleton Loading effect */
    .skeleton {
        background: linear-gradient(90deg, rgba(24, 24, 27, 0.6) 25%, rgba(39, 39, 42, 0.8) 50%, rgba(24, 24, 27, 0.6) 75%);
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
        border-radius: 8px;
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

def create_github_blob(token, repo, content_bytes):
    """Create a git blob on GitHub and return its SHA."""
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
        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 201:
            return {"success": True, "sha": res.json()["sha"]}
        else:
            return {"success": False, "error": res.json().get('message', 'Unknown error')}
    except Exception as e:
        return {"success": False, "error": str(e)}

def upload_batch_to_github(token, repo, branch, folder, file_infos, commit_message, progress_callback=None):
    """Upload a batch of files in a single commit using the Git Database API."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        # 1. Get the latest commit SHA of the branch reference
        ref_url = f"https://api.github.com/repos/{repo}/git/ref/heads/{branch}"
        ref_res = requests.get(ref_url, headers=headers)
        if ref_res.status_code != 200:
            return {"success": False, "error": f"Failed to get branch reference: {ref_res.json().get('message', 'Unknown error')}"}
        
        commit_sha = ref_res.json()["object"]["sha"]
        
        # 2. Get the base tree SHA of that commit
        commit_url = f"https://api.github.com/repos/{repo}/git/commits/{commit_sha}"
        commit_res = requests.get(commit_url, headers=headers)
        if commit_res.status_code != 200:
            return {"success": False, "error": f"Failed to get base commit: {commit_res.json().get('message', 'Unknown error')}"}
            
        base_tree_sha = commit_res.json()["tree"]["sha"]
        
        # 3. Upload all files as blobs in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(create_github_blob, token, repo, img["content"]): img for img in file_infos}
            
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
        tree_res = requests.post(tree_url, headers=headers, json=tree_data)
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
        commit_post_res = requests.post(commit_post_url, headers=headers, json=commit_data)
        if commit_post_res.status_code != 201:
            return {"success": False, "error": f"Failed to create commit: {commit_post_res.json().get('message', 'Unknown error')}"}
            
        new_commit_sha = commit_post_res.json()["sha"]
        
        # 6. Update the branch reference to point to the new commit
        ref_update_url = f"https://api.github.com/repos/{repo}/git/refs/heads/{branch}"
        ref_update_data = {
            "sha": new_commit_sha,
            "force": False
        }
        ref_update_res = requests.patch(ref_update_url, headers=headers, json=ref_update_data)
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
