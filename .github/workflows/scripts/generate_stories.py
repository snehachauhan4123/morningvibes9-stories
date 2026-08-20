import os
import re
import html
import json
import urllib.request
from datetime import datetime
from html.parser import HTMLParser

WP_API_URL = "https://morningvibes9.com/wp-json/wp/v2/posts?per_page=12&_embed"

# Always use the root repository directory
BASE_DIR = os.getcwd()
STORIES_DIR = os.path.join(BASE_DIR, "stories")
INDEX_PATH = os.path.join(BASE_DIR, "index.html")
SITEMAP_PATH = os.path.join(BASE_DIR, "sitemap.xml")

os.makedirs(STORIES_DIR, exist_ok=True)

class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = []
        self.paragraphs = []
        self.current_tag = None
        self.current_data = []

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag.lower()
        self.current_data = []

    def handle_data(self, data):
        self.current_data.append(data)

    def handle_endtag(self, tag):
        text = "".join(self.current_data).strip()
        if text:
            if tag.lower() in ["h1", "h2", "h3"]:
                self.headings.append(text)
            elif tag.lower() == "p":
                self.paragraphs.append(text)
        self.current_tag = None
        self.current_data = []

def clean_text(text):
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def fetch_posts():
    req = urllib.request.Request(
        WP_API_URL,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WebStoriesBot/1.0"}
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))

def extract_slides_from_post(post):
    title = clean_text(post.get("title", {}).get("rendered", "Trending News"))
    content_html = post.get("content", {}).get("rendered", "")
    excerpt_text = clean_text(post.get("excerpt", {}).get("rendered", ""))
    
    featured_img = "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=720&q=80"
    try:
        embedded = post.get("_embedded", {})
        media_list = embedded.get("wp:featuredmedia", [])
        if media_list and isinstance(media_list, list):
            source = media_list[0].get("source_url")
            if source:
                featured_img = source
    except Exception:
        pass

    category = "Trending News"
    try:
        terms = post.get("_embedded", {}).get("wp:term", [])
        if terms and len(terms) > 1 and terms[1]:
            category = terms[1][0].get("name", "Trending News")
    except Exception:
        pass

    extractor = HTMLTextExtractor()
    extractor.feed(content_html)
    
    headings = [clean_text(h) for h in extractor.headings if len(clean_text(h)) > 10]
    paragraphs = [clean_text(p) for p in extractor.paragraphs if len(clean_text(p)) > 25 and "WhatsApp" not in p]

    slides = []
    
    # Slide 1: Cover
    s1_text = excerpt_text if excerpt_text else (paragraphs[0] if paragraphs else "Latest coverage and updates.")
    if len(s1_text) > 140:
        s1_text = s1_text[:137] + "..."
    slides.append({
        "badge": category,
        "heading": title,
        "text": s1_text,
        "image": featured_img
    })
    
    # Slide 2: Key Update
    s2_heading = headings[0] if len(headings) > 0 else "Key Highlights"
    if len(s2_heading) > 70:
        s2_heading = s2_heading[:67] + "..."
    s2_text = paragraphs[0] if paragraphs else "Crucial developments and insider details regarding this breaking story."
    if len(s2_text) > 140:
        s2_text = s2_text[:137] + "..."
    slides.append({
        "badge": "Key Update",
        "heading": s2_heading,
        "text": s2_text,
        "image": featured_img
    })

    # Slide 3: Background & Analysis
    s3_heading = headings[1] if len(headings) > 1 else "What You Need to Know"
    if len(s3_heading) > 70:
        s3_heading = s3_heading[:67] + "..."
    s3_text = paragraphs[1] if len(paragraphs) > 1 else "In-depth insights, expert reactions, and future expectations."
    if len(s3_text) > 140:
        s3_text = s3_text[:137] + "..."
    slides.append({
        "badge": "Analysis",
        "heading": s3_heading,
        "text": s3_text,
        "image": featured_img
    })

    # Slide 4: CTA
    slides.append({
        "badge": "Full Story",
        "heading": "Read The Complete Report",
        "text": "Read full analysis, timeline, live updates, and community discussion on Morning Vibes 9.",
        "image": featured_img
    })

    return {
        "slug": post.get("slug"),
        "title": title,
        "link": post.get("link"),
        "date": post.get("date", datetime.now().isoformat()),
        "image": featured_img,
        "category": category,
        "slides": slides
    }

def generate_story_html(story):
    slides = story["slides"]
    pages_html = ""
    
    for i, slide in enumerate(slides):
        is_last = (i == len(slides) - 1)
        auto_advance = 'auto-advance-after="6s"' if not is_last else ''
        
        cta_markup = ""
        if is_last:
            cta_markup = f'''
      <amp-story-page-outlink layout="nodisplay" theme="custom" cta-accent-color="#094fa7" cta-accent-element="text">
        <a href="{story['link']}" target="_blank">Read Full Article on Morning Vibes 9</a>
      </amp-story-page-outlink>
            '''

        pages_html += f'''
    <!-- Slide {i+1} -->
    <amp-story-page id="slide-{i+1}" {auto_advance}>
      <amp-story-grid-layer template="fill">
        <amp-img src="{slide['image']}" width="720" height="1280" layout="responsive" alt="{html.escape(slide['heading'])}"></amp-img>
      </amp-story-grid-layer>
      <div class="scrim-overlay"></div>
      <amp-story-grid-layer template="vertical" class="content-box">
        <span class="tag-badge" animate-in="fade-in">{html.escape(slide['badge'])}</span>
        <h2 class="story-heading" animate-in="fly-in-bottom">{html.escape(slide['heading'])}</h2>
        <p class="story-desc" animate-in="fly-in-bottom" animate-in-delay="0.2s">{html.escape(slide['text'])}</p>
        {"<div class='swipe-hint' animate-in='fade-in' animate-in-delay='0.5s'>👉 Tap to continue</div>" if not is_last else ""}
      </amp-story-grid-layer>
      {cta_markup}
    </amp-story-page>
        '''

    story_url = f"https://stories.morningvibes9.com/stories/{story['slug']}/"
    
    return f'''<!doctype html>
<html ⚡ lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(story['title'])} - Morning Vibes 9</title>
  <link rel="canonical" href="{story_url}">
  <meta name="viewport" content="width=device-width,minimum-scale=1,initial-scale=1">
  
  <!-- AMP Scripts -->
  <script async src="https://cdn.ampproject.org/v0.js"></script>
  <script async custom-element="amp-story" src="https://cdn.ampproject.org/v0/amp-story-1.0.js"></script>
  <script async custom-element="amp-analytics" src="https://cdn.ampproject.org/v0/amp-analytics-0.1.js"></script>

  <!-- Google Discover SEO Schema -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    "mainEntityOfPage": "{story_url}",
    "headline": "{html.escape(story['title'])}",
    "image": ["{story['image']}"],
    "datePublished": "{story['date']}",
    "dateModified": "{story['date']}",
    "author": {{
      "@type": "Organization",
      "name": "Morning Vibes 9",
      "url": "https://morningvibes9.com"
    }},
    "publisher": {{
      "@type": "NewsMediaOrganization",
      "name": "Morning Vibes 9",
      "logo": {{
        "@type": "ImageObject",
        "url": "https://morningvibes9.com/wp-content/uploads/2025/08/Logo@450x200-1-e1758982931221.png"
      }}
    }},
    "description": "{html.escape(story['slides'][0]['text'])}"
  }}
  </script>

  <style amp-custom>
    amp-story {{
      font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
      color: #ffffff;
    }}
    .scrim-overlay {{
      position: absolute;
      top: 0; left: 0; right: 0; bottom: 0;
      background: linear-gradient(
        to bottom,
        rgba(0, 0, 0, 0.4) 0%,
        rgba(0, 0, 0, 0.1) 40%,
        rgba(0, 0, 0, 0.85) 75%,
        rgba(0, 0, 0, 0.98) 100%
      );
      z-index: 1;
    }}
    .content-box {{
      z-index: 2;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      padding: 24px 20px 48px;
    }}
    .tag-badge {{
      display: inline-block;
      align-self: flex-start;
      background: #e11d48;
      color: #ffffff;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      padding: 4px 10px;
      border-radius: 4px;
      margin-bottom: 12px;
      letter-spacing: 0.5px;
    }}
    .story-heading {{
      font-size: 23px;
      font-weight: 800;
      line-height: 1.25;
      margin: 0 0 12px 0;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.8);
    }}
    .story-desc {{
      font-size: 15px;
      font-weight: 400;
      line-height: 1.45;
      color: #f1f5f9;
      margin: 0;
      text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8);
    }}
    .swipe-hint {{
      font-size: 12px;
      color: #cbd5e1;
      margin-top: 14px;
      text-transform: uppercase;
      letter-spacing: 1px;
    }}
  </style>
  <style amp-boilerplate>body{{-webkit-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-moz-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-ms-animation:-amp-start 8s steps(1,end) 0s 1 normal both;animation:-amp-start 8s steps(1,end) 0s 1 normal both}}@-webkit-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@-moz-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@-ms-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@-o-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}</style><noscript><style amp-boilerplate>body{{-webkit-animation:none;-moz-animation:none;-ms-animation:none;animation:none}}</style></noscript>
</head>
<body>
  <amp-story
    standalone
    title="{html.escape(story['title'])}"
    publisher="Morning Vibes 9"
    publisher-logo-src="https://morningvibes9.com/wp-content/uploads/2025/08/Logo@450x200-1-e1758982931221.png"
    poster-portrait-src="{story['image']}">
    {pages_html}
  </amp-story>
</body>
</html>
'''

def update_hub_and_sitemap(all_stories):
    sitemap_entries = [
        '  <url>\n    <loc>https://stories.morningvibes9.com/</loc>\n    <changefreq>daily</changefreq>\n    <priority>1.0</priority>\n  </url>'
    ]
    cards_html = ""
    
    for s in all_stories:
        slug = s["slug"]
        sitemap_entries.append(
            f'  <url>\n    <loc>https://stories.morningvibes9.com/stories/{slug}/</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>'
        )
        cards_html += f'''
    <a href="/stories/{slug}/" class="story-card">
      <div class="thumbnail-wrapper">
        <span class="story-badge">⚡ Story</span>
        <img src="{s['image']}" alt="{html.escape(s['title'])}" loading="lazy">
      </div>
      <div class="story-info">
        <h3>{html.escape(s['title'])}</h3>
        <p class="story-meta">{html.escape(s['category'])}</p>
      </div>
    </a>'''

    sitemap_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(sitemap_entries)}
</urlset>'''

    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write(sitemap_content)

    hub_html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Web Stories - Morning Vibes 9</title>
  <meta name="description" content="Visual Web Stories on trending news, technology, economy, and global events by Morning Vibes 9.">
  <link rel="canonical" href="https://stories.morningvibes9.com/">
  <link rel="icon" href="https://morningvibes9.com/wp-content/uploads/2025/09/cropped-Fav_icon-32x32.png" sizes="32x32">
  <style>
    :root {{ --primary: #094fa7; --dark: #0f172a; --card-bg: #ffffff; --bg: #f8fafc; --text: #1e293b; --text-muted: #64748b; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: var(--bg); color: var(--text); line-height: 1.5; }}
    header {{ background: #ffffff; border-bottom: 1px solid #e2e8f0; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; }}
    .logo img {{ max-height: 42px; width: auto; display: block; }}
    .main-site-btn {{ background: var(--primary); color: #ffffff; text-decoration: none; font-size: 14px; font-weight: 600; padding: 8px 16px; border-radius: 6px; }}
    .hero {{ text-align: center; padding: 40px 20px 20px; }}
    .hero h1 {{ font-size: 28px; font-weight: 800; color: var(--dark); margin-bottom: 8px; }}
    .hero p {{ color: var(--text-muted); font-size: 16px; }}
    .stories-grid {{ max-width: 1200px; margin: 30px auto; padding: 0 20px; display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 24px; }}
    .story-card {{ background: var(--card-bg); border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-decoration: none; color: inherit; display: flex; flex-direction: column; transition: transform 0.2s ease; }}
    .story-card:hover {{ transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }}
    .thumbnail-wrapper {{ position: relative; aspect-ratio: 9/16; width: 100%; background: #e2e8f0; }}
    .thumbnail-wrapper img {{ width: 100%; height: 100%; object-fit: cover; }}
    .story-badge {{ position: absolute; top: 12px; left: 12px; background: rgba(15,23,42,0.85); color: #fff; font-size: 11px; font-weight: 700; padding: 4px 8px; border-radius: 4px; text-transform: uppercase; }}
    .story-info {{ padding: 16px; }}
    .story-info h3 {{ font-size: 15px; font-weight: 700; color: var(--dark); line-height: 1.35; margin-bottom: 6px; }}
    .story-meta {{ font-size: 12px; color: var(--text-muted); }}
    footer {{ text-align: center; padding: 40px 20px; font-size: 14px; color: var(--text-muted); border-top: 1px solid #e2e8f0; margin-top: 60px; background: #ffffff; }}
    footer a {{ color: var(--primary); text-decoration: none; }}
  </style>
</head>
<body>
  <header>
    <a href="https://morningvibes9.com/" class="logo">
      <img src="https://morningvibes9.com/wp-content/uploads/2025/08/Logo@450x200-1-e1758982931221.png" alt="Morning Vibes 9">
    </a>
    <a href="https://morningvibes9.com/" class="main-site-btn">Visit Website →</a>
  </header>
  <section class="hero">
    <h1>Visual Web Stories</h1>
    <p>Tap, swipe, and explore quick stories on trending news and insights.</p>
  </section>
  <main class="stories-grid">
{cards_html}
  </main>
  <footer>
    <p>© 2026 <a href="https://morningvibes9.com/">Morning Vibes 9</a>. All rights reserved.</p>
  </footer>
</body>
</html>'''

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(hub_html)

def main():
    print("Fetching latest posts from Morning Vibes 9...")
    posts = fetch_posts()
    processed_stories = []
    
    for p in posts:
        story = extract_slides_from_post(p)
        slug = story["slug"]
        if not slug:
            continue
        
        story_folder = os.path.join(STORIES_DIR, slug)
        os.makedirs(story_folder, exist_ok=True)
        story_file = os.path.join(story_folder, "index.html")
        
        story_html = generate_story_html(story)
        with open(story_file, "w", encoding="utf-8") as f:
            f.write(story_html)
        
        processed_stories.append(story)
        print(f"Generated story: {slug}")
        
    update_hub_and_sitemap(processed_stories)
    print(f"Successfully generated {len(processed_stories)} stories and updated hub + sitemap!")

if __name__ == "__main__":
    main()
