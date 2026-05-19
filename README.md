# 🖼️ ImageSync Public | Global Image Hosting

A high-performance, professional-grade web dashboard designed for developers and creators who need a fast, secure, and reliable way to optimize, compress, and host images directly on GitHub. 

Built with **Streamlit**, **Pillow**, and the **GitHub Git Database REST API**, it offers an atomic, single-commit workflow from your local device to your repository—with no local Git or complex command line tools required.

---

## ✨ Features

- 🏎️ **Supercharged Local Optimization**: Multi-threaded image processing converts PNGs, JPGs, JPEGs, and WebPs to highly optimized **WebP** files in parallel.
- 📦 **Single-Commit Atomic Batches**: Uploads multiple images in a **single commit** using the GitHub Git Database API, keeping your repository history clean and avoiding standard 409 reference/HEAD race conditions.
- 🎨 **WebP Quality Slider**: Custom compression quality slider (10% to 100%) to perfectly balance file size and visual fidelity.
- 🏷️ **Bulk Renaming Pattern**: Pre-filled bulk renaming options to clean up screenshots or assets into consistent naming structures (e.g., `project-1.webp`, `project-2.webp`).
- 🔒 **Zero-Trust Security**: No server logs or databases. Your GitHub Personal Access Token (PAT) resides completely in session RAM and is wiped clean on reload.
- 📱 **Mobile & Desktop Responsive**: Clean glassmorphism layout, styled with rich CSS variables, optimized for both desktop browsers and mobile phones.

---

## 🛡️ Security & Privacy

> [!IMPORTANT]
> **Your security and privacy are guaranteed.**
> - **In-Memory Only**: Your GitHub PAT is only ever held in RAM during active API transactions and is never written to disk or sent to a third party.
> - **No Tracking**: There are no databases, analytics tracking, or logs attached to this application.
> - **Session Erasure**: Refreshing your browser tab completely purges all tokens and state.

---

## 📖 Step-by-Step Tutorial & Use Case

Here is how you can use **ImageSync Public** to optimize and host assets for a personal blog, repository, or portfolio page.

### Use Case Example: Hosting Blog Post Images
Let's say you have a repository called `my-portfolio` and you want to host images for a new project card.

#### Step 1: Generate a GitHub Personal Access Token (PAT)
1. Go to your GitHub account **Settings > Developer Settings > Personal Access Tokens > Tokens (classic)**.
2. Click **Generate new token (classic)**.
3. Give it a descriptive name (e.g., `ImageSync Hosting`) and check the **`repo`** scope (this is required to write contents to your repository).
4. Click **Generate token** and copy the resulting string. Keep it safe!

#### Step 2: Configure the Sidebar in the App
1. Paste your **GitHub PAT** into the first field.
2. Enter your **Repository Path** (e.g., `your-username/my-portfolio`).
3. Set your **Target Branch** (e.g., `main` or `gh-pages`).
4. Set the **Target Folder** (e.g., `assets/images`). The folder will be automatically created if it doesn't exist.
5. (Optional) Set a **Base Filename** (e.g., `portfolio-project`) if you want your files cleanly auto-numbered (e.g., `portfolio-project-1.webp`, `portfolio-project-2.webp`).

#### Step 3: Drag & Drop Images & Sync
1. Drag and drop or browse the images you want to host.
2. Adjust the WebP Quality slider (80% is the recommended default for outstanding quality-to-size balance).
3. Click **🚀 Process & Deploy**.
4. The dashboard will process all images in parallel, upload them to your repository as a single git commit, and present a gallery of live links.
5. Copy the generated `raw.githubusercontent.com` URLs directly into your markdown or HTML files!

---

## 💻 Running Locally

You can spin up your own instance locally in three simple steps:

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/image-hosting-pub.git
cd image-hosting-pub
```

### 2. Install Dependencies
Make sure you have Python 3.8+ installed.
```bash
pip install -r requirements.txt
```

### 3. Start the Server
```bash
streamlit run app.py
```
This will automatically open the app in your default browser at `http://localhost:8501`.

---

## 🚀 How to Fork & Deploy to Streamlit Cloud (Personal Version)

If you want your repository paths or target folders to be pre-filled so you don't have to type them every time, you can deploy your own instance for free:

1. **Fork** this repository to your own GitHub account.
2. Go to **[Streamlit Community Cloud](https://share.streamlit.io/)** and log in with your GitHub account.
3. Click **New App**, select your forked repository, the branch (`main`), and set the main file path to `app.py`.
4. Click **Deploy!**
5. **Pre-fill Defaults (Optional)**: If you want to customize default values, you can edit the sidebar text inputs in `app.py` directly, or configure environment secrets in Streamlit Cloud.

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.
