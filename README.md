# Morning Vibes 9 - Web Stories Repository

This repository hosts standalone, high-performance **Google AMP Web Stories** for [Morning Vibes 9](https://morningvibes9.com) on GitHub Pages (`stories.morningvibes9.com`).

---

## 📁 Repository Structure

```text
├── CNAME                         # Configures custom domain: stories.morningvibes9.com
├── index.html                    # Visual Web Stories Hub / Catalog
├── sitemap.xml                   # XML sitemap for Google Search Console
├── templates/
│   └── story-template.html       # Master reusable AMP Web Story template
└── stories/
    └── trump-west-asia-speech/   # Individual story folder
        └── index.html            # Story AMP HTML file
```

---

## 🚀 How to Deploy to GitHub (One-Time Setup)

### Step 1: Create a GitHub Repository
1. Log into your [GitHub Account](https://github.com/new).
2. Create a new repository named `morningvibes9-stories` (Set to **Public**).

### Step 2: Push These Files to GitHub
Open your terminal inside this project directory and run:
```bash
git init
git add .
git commit -m "Initial commit: Morning Vibes 9 Web Stories"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/morningvibes9-stories.git
git push -u origin main
```

### Step 3: Enable GitHub Pages
1. Go to your GitHub repository **Settings** → **Pages**.
2. Under **Build and deployment**:
   - Source: **Deploy from a branch**
   - Branch: **`main`** / Folder: **`/ (root)`** → Click **Save**.
3. Under **Custom domain**:
   - Enter: `stories.morningvibes9.com`
   - Click **Save**.
   - Check **Enforce HTTPS** (Wait a few minutes for SSL certificate issuance).

---

## 🌐 How to Connect Hostinger DNS (One-Time Setup)

To point `stories.morningvibes9.com` to GitHub Pages:

1. Log into **Hostinger hPanel**.
2. Go to **Domains** → `morningvibes9.com` → **DNS / Nameservers**.
3. Under **Manage DNS Records**, add a new **CNAME Record**:
   - **Type:** `CNAME`
   - **Name:** `stories`
   - **Target:** `YOUR_GITHUB_USERNAME.github.io.` *(Replace with your GitHub username, end with a dot if requested)*
   - **TTL:** `14400` (or default)
4. Click **Add Record**.

---

## ✍️ How to Publish a New Web Story

Whenever you want to publish a new story:
1. Duplicate `templates/story-template.html`.
2. Create a new folder inside `stories/` (e.g., `stories/new-topic-slug/`).
3. Save your file as `stories/new-topic-slug/index.html`.
4. Fill in the title, text, images, and CTA link back to your blog post.
5. Add the link to `index.html` (hub) and `sitemap.xml`.
6. Push to GitHub (`git add . && git commit -m "Add new story" && git push`). It goes live immediately!
