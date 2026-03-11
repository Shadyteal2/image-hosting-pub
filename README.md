# 🚀 ImageSync Public | Global Image Hosting

<div align="center">
  <a href="https://image-hosting-byshady.streamlit.app/">
    <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" width="350" alt="Open the Site">
  </a>
  <br><br>
  <img src="https://raw.githubusercontent.com/Shadyteal2/image-hosting-pub/main/assets/ImageSync.jpeg" width="95%" alt="ImageSync Preview">
</div>

---

### 🌐 [Live Application](https://image-hosting-byshady.streamlit.app/)

**ImageSync Public** is a professional-grade, high-performance web dashboard designed for developers and creators who need a fast way to optimize and host images directly on GitHub. 

Built with **Streamlit**, **Pillow**, and the **GitHub REST API**, it offers a seamless workflow from your local device to the world—no local Git required.

---

## ✨ Features

- 🏎️ **Super Fast**: Multi-threaded image processing and API uploads.
- 🎨 **WebP Optimization**: Automatically converts images to WebP (customizable compression) for maximum performance.
- 📱 **Mobile Ready**: Runs in the browser; host images directly from your phone.
- 🔒 **Privacy Focused**: No data collection. Credentials stay in session memory and vanish on reload.
- 🛠️ **Developer Pro**: Get instant `raw.githubusercontent.com` links for your sites.

---

## 🛡️ Privacy & Security

> [!IMPORTANT]
> **We value your security.** 
> - **Zero Persistence**: Your GitHub PAT is only held in the application's RAM during your session. 
> - **No Tracking**: We do not collect, store, or log any of your personal data or uploaded images.
> - **Session Reset**: As soon as you refresh or close the tab, all credentials and session states are wiped clean.

---

## 🚀 Deployment Guide

### Use the Public Site
Simply visit [ImageSync Public](https://image-hosting-byshady.streamlit.app/), enter your GitHub PAT and Repository details in the sidebar, and start syncing!

### Deploy Your Own (Personal)
Want a version that already has your repo details? It's easy:
1. **Fork** this repository.
2. Go to **[Streamlit Community Cloud](https://share.streamlit.io/)**.
3. Deploy your forked repository.
4. **(Optional Pro Tip)**: Add your `GITHUB_TOKEN` and repo details to the **Secrets** manager in Streamlit if you want it pre-filled!

---

## 💻 Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<div align="center">
  Made with 💜 by ShadyBilla
</div>
