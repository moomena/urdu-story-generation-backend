# # import os
# # import time
# # import re
# # from selenium import webdriver
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC
# # from webdriver_manager.chrome import ChromeDriverManager

# # # ─── CONFIG ───────────────────────────────────────────────────────────────────
# # OUTPUT_DIR = "stories"
# # os.makedirs(OUTPUT_DIR, exist_ok=True)

# # # ─── DRIVER SETUP ─────────────────────────────────────────────────────────────

# # def get_driver():
# #     driver = webdriver.Safari()
# #     return driver

# # # ─── HELPERS ──────────────────────────────────────────────────────────────────
# # def is_urdu(text):
# #     """Check if text contains substantial Urdu content."""
# #     urdu_chars = len(re.findall(r'[\u0600-\u06FF]', text))
# #     return urdu_chars > 50  # at least 50 Urdu characters

# # def clean_text(text):
# #     """Remove non-Urdu junk: English, HTML artifacts, extra whitespace."""
# #     # Remove english characters and latin punctuation (keep Urdu punctuation)
# #     text = re.sub(r'[a-zA-Z0-9]', '', text)
# #     # Remove URLs
# #     text = re.sub(r'http\S+', '', text)
# #     # Collapse multiple newlines/spaces
# #     text = re.sub(r'\n{3,}', '\n\n', text)
# #     text = re.sub(r'[ \t]+', ' ', text)
# #     return text.strip()

# # def save_story(story_id, title, content):
# #     """Save a story to its own .txt file."""
# #     filename = os.path.join(OUTPUT_DIR, f"story_{story_id:04d}.txt")
# #     with open(filename, "w", encoding="utf-8") as f:
# #         f.write(f"{title}\n\n{content}")
# #     print(f"  ✅ Saved: story_{story_id:04d}.txt  ({len(content)} chars)")

# # # ─── SCRAPER 1: urdupoint.com ─────────────────────────────────────────────────
# # def scrape_urdupoint(driver, start_id=1):
# #     """
# #     Scrapes Urdu children's stories from urdupoint.com/kids/story
# #     Returns next available story_id.
# #     """
# #     print("\n📖 Scraping urdupoint.com ...")
# #     story_id = start_id
    
# #     # Category pages listing stories
# #     base_urls = [
# #         "https://www.urdupoint.com/kids/story/kids-urdu-stories.html",
# #         "https://www.urdupoint.com/kids/story/urdu-moral-stories.html",
# #         "https://www.urdupoint.com/kids/story/urdu-fairy-tales.html",
# #     ]

# #     story_links = []

# #     for cat_url in base_urls:
# #         try:
# #             driver.get(cat_url)
# #             time.sleep(2)
# #             anchors = driver.find_elements(By.CSS_SELECTOR, "a[href*='/kids/story/']")
# #             for a in anchors:
# #                 href = a.get_attribute("href")
# #                 if href and href not in story_links and href != cat_url:
# #                     story_links.append(href)
# #         except Exception as e:
# #             print(f"  ⚠️  Failed to load category {cat_url}: {e}")

# #     print(f"  Found {len(story_links)} story links on urdupoint.com")

# #     for link in story_links:
# #         if story_id - start_id >= 150:   # cap at 150 stories from this source
# #             break
# #         try:
# #             driver.get(link)
# #             time.sleep(1.5)

# #             # Title
# #             try:
# #                 title = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
# #             except:
# #                 title = f"کہانی {story_id}"

# #             # Story body — urdupoint wraps story in .article-text or .urdu-content
# #             content = ""
# #             for selector in [".article-text", ".urdu-content", ".story-content", "article"]:
# #                 try:
# #                     el = driver.find_element(By.CSS_SELECTOR, selector)
# #                     content = el.text.strip()
# #                     if len(content) > 100:
# #                         break
# #                 except:
# #                     continue

# #             if not content:
# #                 # fallback: grab all paragraphs
# #                 paras = driver.find_elements(By.TAG_NAME, "p")
# #                 content = "\n\n".join(p.text.strip() for p in paras if p.text.strip())

# #             content = clean_text(content)

# #             if not is_urdu(content):
# #                 print(f"  ⏭️  Skipped (not Urdu): {link}")
# #                 continue

# #             save_story(story_id, title, content)
# #             story_id += 1

# #         except Exception as e:
# #             print(f"  ⚠️  Error on {link}: {e}")

# #     return story_id

# # # ─── SCRAPER 2: urdunama.com ──────────────────────────────────────────────────
# # def scrape_urdunama(driver, start_id=1):
# #     """
# #     Scrapes Urdu stories from urdunama.com
# #     Returns next available story_id.
# #     """
# #     print("\n📖 Scraping urdunama.com ...")
# #     story_id = start_id

# #     base_url = "https://urdunama.com/category/bachon-ki-kahanyan/"
# #     story_links = []

# #     # Paginate through listing pages
# #     for page in range(1, 10):
# #         try:
# #             url = base_url if page == 1 else f"{base_url}page/{page}/"
# #             driver.get(url)
# #             time.sleep(2)
# #             anchors = driver.find_elements(By.CSS_SELECTOR, "h2.entry-title a, h3.entry-title a")
# #             if not anchors:
# #                 print(f"  No more pages at page {page}")
# #                 break
# #             for a in anchors:
# #                 href = a.get_attribute("href")
# #                 if href and href not in story_links:
# #                     story_links.append(href)
# #         except Exception as e:
# #             print(f"  ⚠️  Pagination error page {page}: {e}")
# #             break

# #     print(f"  Found {len(story_links)} story links on urdunama.com")

# #     for link in story_links:
# #         if story_id - start_id >= 100:  # cap at 100 stories from this source
# #             break
# #         try:
# #             driver.get(link)
# #             time.sleep(1.5)

# #             try:
# #                 title = driver.find_element(By.CSS_SELECTOR, "h1.entry-title").text.strip()
# #             except:
# #                 title = f"کہانی {story_id}"

# #             content = ""
# #             for selector in [".entry-content", ".post-content", "article .content"]:
# #                 try:
# #                     el = driver.find_element(By.CSS_SELECTOR, selector)
# #                     content = el.text.strip()
# #                     if len(content) > 100:
# #                         break
# #                 except:
# #                     continue

# #             if not content:
# #                 paras = driver.find_elements(By.TAG_NAME, "p")
# #                 content = "\n\n".join(p.text.strip() for p in paras if p.text.strip())

# #             content = clean_text(content)

# #             if not is_urdu(content):
# #                 print(f"  ⏭️  Skipped (not Urdu): {link}")
# #                 continue

# #             save_story(story_id, title, content)
# #             story_id += 1

# #         except Exception as e:
# #             print(f"  ⚠️  Error on {link}: {e}")

# #     return story_id

# # # ─── MAIN ─────────────────────────────────────────────────────────────────────
# # def main():
# #     driver = get_driver()
# #     try:
# #         next_id = scrape_urdupoint(driver, start_id=1)
# #         next_id = scrape_urdunama(driver, start_id=next_id)
# #         print(f"\n🎉 Done! Total stories saved: {next_id - 1}  →  ./{OUTPUT_DIR}/")
# #     finally:
# #         driver.quit()

# # if __name__ == "__main__":
# #     main()
# """
# UrduPoint Urdu Children's Stories Scraper  ─ Safari version (Mac)
# Phase I - Dataset Collection
# """

# import re
# import time
# import json
# import unicodedata
# import logging
# from pathlib import Path

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from tqdm import tqdm

# # ── Configuration ──────────────────────────────────────────────────────────────
# OUTPUT_DIR   = Path("urdu_stories_raw")
# OUTPUT_FILE  = Path("corpus.txt")
# MIN_STORIES  = 200
# PAGE_LOAD_WAIT = 4
# MAX_PAGES      = 20

# # Special tokens
# EOS_TOKEN = "\uE001"
# EOP_TOKEN = "\uE002"
# EOT_TOKEN = "\uE003"

# BASE_URL = "https://www.urdupoint.com"

# CATEGORIES = [
#     "moral-stories",
#     "funny-stories",
#     "true-stories",
#     "kids-urdu-stories",
#     "urdu-fairy-tales",
# ]

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s",
# )
# log = logging.getLogger(__name__)


# # ── Safari driver setup ────────────────────────────────────────────────────────
# def make_driver() -> webdriver.Safari:
#     driver = webdriver.Safari()
#     driver.maximize_window()
#     return driver


# # ── Urdu text utilities ────────────────────────────────────────────────────────
# URDU_RE = re.compile(
#     r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]'
# )

# def is_mostly_urdu(text: str, threshold: float = 0.35) -> bool:
#     chars = [c for c in text if not c.isspace()]
#     if not chars:
#         return False
#     return sum(1 for c in chars if URDU_RE.match(c)) / len(chars) >= threshold


# def normalize_urdu(text: str) -> str:
#     text = unicodedata.normalize("NFC", text)
#     text = re.sub(r'https?://\S+', '', text)
#     text = re.sub(r'&[a-zA-Z]+;|&#\d+;', ' ', text)
#     text = re.sub(r'[a-zA-Z0-9]+', '', text)
#     text = re.sub(r'\n{2,}', '\n\n', text)
#     text = re.sub(r'[ \t]+', ' ', text)
#     return text.strip()


# def add_special_tokens(text: str) -> str:
#     text = re.sub(r'([۔؟!])\s*', rf'\1{EOS_TOKEN} ', text)
#     text = re.sub(r'\n\n+', f' {EOP_TOKEN}\n', text)
#     text = re.sub(r'\n', ' ', text)
#     text = re.sub(r' +', ' ', text).strip()
#     return text + f' {EOT_TOKEN}'


# # ── Listing page: extract story links ─────────────────────────────────────────
# def get_story_links(driver: webdriver.Safari, url: str) -> list[str]:
#     log.info("  Listing: %s", url)
#     driver.get(url)
#     time.sleep(PAGE_LOAD_WAIT)

#     links = set()
#     try:
#         for a in driver.find_elements(By.CSS_SELECTOR, "a.sharp_box"):
#             href = a.get_attribute("href") or ""
#             if "/kids/detail/" in href:
#                 links.add(href)
#     except Exception as e:
#         log.warning("  Link extraction error: %s", e)

#     log.info("  → %d story links found", len(links))
#     return list(links)


# def collect_all_urls(driver: webdriver.Safari) -> list[str]:
#     all_links: set[str] = set()

#     for cat in CATEGORIES:
#         log.info("=== Category: %s ===", cat)
#         for page_num in range(1, MAX_PAGES + 1):
#             if page_num == 1:
#                 url = f"{BASE_URL}/kids/category/{cat}.html"
#             else:
#                 url = f"{BASE_URL}/kids/category/{cat}-page{page_num}.html"

#             links = get_story_links(driver, url)

#             if not links:
#                 log.info("  No links on page %d — done with category.", page_num)
#                 break

#             all_links.update(links)
#             log.info("  Cumulative total: %d URLs", len(all_links))
#             time.sleep(1.5)

#     return list(all_links)


# # ── Story page: extract & clean story text ────────────────────────────────────
# def extract_story(driver: webdriver.Safari, url: str) -> dict | None:
#     driver.get(url)
#     time.sleep(PAGE_LOAD_WAIT)

#     title = ""
#     for selector in ["h2.urdu", "h1.phead", "h1"]:
#         try:
#             el = driver.find_element(By.CSS_SELECTOR, selector)
#             title = el.text.strip()
#             if title:
#                 break
#         except Exception:
#             continue

#     text = None
#     for selector in ["div.txt_detail", "div.detail_txt", "div.news_article"]:
#         try:
#             el = driver.find_element(By.CSS_SELECTOR, selector)
#             candidate = el.text.strip()
#             if len(candidate) > 100:
#                 text = candidate
#                 break
#         except Exception:
#             continue

#     if not text:
#         log.warning("  No content found at %s", url)
#         return None

#     text = normalize_urdu(text)

#     if not is_mostly_urdu(text):
#         log.debug("  Skipping — insufficient Urdu content")
#         return None

#     if len(text) < 100:
#         log.debug("  Too short, skipping")
#         return None

#     return {
#         "title": title,
#         "url":   url,
#         "text":  add_special_tokens(text),
#     }


# # ── Main ───────────────────────────────────────────────────────────────────────
# def main():
#     OUTPUT_DIR.mkdir(exist_ok=True)

#     log.info("Launching Safari...")
#     driver = make_driver()

#     try:
#         log.info("Step 1: Collecting story URLs...")
#         urls = collect_all_urls(driver)
#         log.info("Total story URLs found: %d", len(urls))

#         if len(urls) < MIN_STORIES:
#             log.warning("Only %d URLs found (target: %d).", len(urls), MIN_STORIES)

#         Path("story_urls.json").write_text(
#             json.dumps(urls, ensure_ascii=False, indent=2), encoding="utf-8"
#         )
#         log.info("URL list saved → story_urls.json")

#         log.info("Step 2: Scraping %d stories...", len(urls))
#         stories: list[dict] = []

#         for url in tqdm(urls, desc="Scraping stories"):
#             slug = url.rstrip("/").split("/")[-1].replace(".html", "")
#             cache_path = OUTPUT_DIR / f"{slug}.json"

#             if cache_path.exists():
#                 stories.append(json.loads(cache_path.read_text(encoding="utf-8")))
#                 continue

#             story = extract_story(driver, url)
#             if story:
#                 cache_path.write_text(
#                     json.dumps(story, ensure_ascii=False, indent=2), encoding="utf-8"
#                 )
#                 stories.append(story)
#                 log.info("  ✓ %-60s  (%d chars)", story["title"] or slug, len(story["text"]))
#             else:
#                 log.warning("  ✗ Failed: %s", slug)

#             time.sleep(1.2)

#         log.info("Step 3: Writing output files...")

#         Path("stories.json").write_text(
#             json.dumps(stories, ensure_ascii=False, indent=2), encoding="utf-8"
#         )
#         log.info("JSON dataset saved → stories.json  (%d stories)", len(stories))

#         with OUTPUT_FILE.open("w", encoding="utf-8") as f:
#             for story in stories:
#                 f.write(story["text"] + "\n")

#         log.info("Done ✓  |  Stories: %d  |  Corpus: %s  (%d bytes)",
#                  len(stories), OUTPUT_FILE, OUTPUT_FILE.stat().st_size)

#     finally:
#         driver.quit()
#         log.info("Browser closed.")


# if __name__ == "__main__":
#     main()
"""
UrduPoint Urdu Children's Stories Scraper — Safari version (Mac)
Phase I - Dataset Collection (continuation run — skips already scraped stories)
"""

import re
import time
import json
import unicodedata
import logging
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from tqdm import tqdm

# ── Configuration ──────────────────────────────────────────────────────────────
OUTPUT_DIR   = Path("urdu_stories_raw")       # existing cache folder
OUTPUT_FILE  = Path("corpus.txt")
TARGET       = 200
PAGE_LOAD_WAIT = 4
MAX_PAGES      = 20

# Special tokens
EOS_TOKEN = "\uE001"
EOP_TOKEN = "\uE002"
EOT_TOKEN = "\uE003"

BASE_URL = "https://www.urdupoint.com"

# ── Add more categories to find new stories ────────────────────────────────────
CATEGORIES = [
    "moral-stories",
    "funny-stories",
    "true-stories",
    "kids-urdu-stories",
    "urdu-fairy-tales",
    "bachon-ki-kahanyan",
    "islami-kahanyan",
    "sabaq-amoz-kahanyan",
    "urdu-short-stories",
    "historical-stories",
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


# ── Safari driver ──────────────────────────────────────────────────────────────
def make_driver() -> webdriver.Safari:
    driver = webdriver.Safari()
    driver.maximize_window()
    return driver


# ── Urdu text utilities ────────────────────────────────────────────────────────
URDU_RE = re.compile(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]')

def is_mostly_urdu(text: str, threshold: float = 0.35) -> bool:
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return False
    return sum(1 for c in chars if URDU_RE.match(c)) / len(chars) >= threshold

def normalize_urdu(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'&[a-zA-Z]+;|&#\d+;', ' ', text)
    text = re.sub(r'[a-zA-Z0-9]+', '', text)
    text = re.sub(r'\n{2,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def add_special_tokens(text: str) -> str:
    text = re.sub(r'([۔؟!])\s*', rf'\1{EOS_TOKEN} ', text)
    text = re.sub(r'\n\n+', f' {EOP_TOKEN}\n', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r' +', ' ', text).strip()
    return text + f' {EOT_TOKEN}'


# ── Listing page ───────────────────────────────────────────────────────────────
def get_story_links(driver, url: str) -> list[str]:
    log.info("  Listing: %s", url)
    driver.get(url)
    time.sleep(PAGE_LOAD_WAIT)
    links = set()
    try:
        for a in driver.find_elements(By.CSS_SELECTOR, "a.sharp_box"):
            href = a.get_attribute("href") or ""
            if "/kids/detail/" in href:
                links.add(href)
    except Exception as e:
        log.warning("  Link extraction error: %s", e)
    log.info("  → %d links found", len(links))
    return list(links)

def collect_all_urls(driver) -> list[str]:
    all_links: set[str] = set()
    for cat in CATEGORIES:
        log.info("=== Category: %s ===", cat)
        for page_num in range(1, MAX_PAGES + 1):
            url = (f"{BASE_URL}/kids/category/{cat}.html" if page_num == 1
                   else f"{BASE_URL}/kids/category/{cat}-page{page_num}.html")
            links = get_story_links(driver, url)
            if not links:
                log.info("  No links on page %d — done with category.", page_num)
                break
            all_links.update(links)
            log.info("  Cumulative total: %d URLs", len(all_links))
            time.sleep(1.5)
    return list(all_links)


# ── Story page ─────────────────────────────────────────────────────────────────
def extract_story(driver, url: str) -> dict | None:
    driver.get(url)
    time.sleep(PAGE_LOAD_WAIT)

    title = ""
    for selector in ["h2.urdu", "h1.phead", "h1"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, selector)
            title = el.text.strip()
            if title:
                break
        except Exception:
            continue

    text = None
    for selector in ["div.txt_detail", "div.detail_txt", "div.news_article"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, selector)
            candidate = el.text.strip()
            if len(candidate) > 100:
                text = candidate
                break
        except Exception:
            continue

    if not text:
        log.warning("  No content at %s", url)
        return None

    text = normalize_urdu(text)
    if not is_mostly_urdu(text) or len(text) < 100:
        return None

    return {"title": title, "url": url, "text": add_special_tokens(text)}


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Count what we already have
    existing = list(OUTPUT_DIR.glob("*.json"))
    log.info("Already scraped: %d stories in %s", len(existing), OUTPUT_DIR)

    if len(existing) >= TARGET:
        log.info("Already at target (%d). Nothing to do.", TARGET)
        return

    already_scraped_slugs = {p.stem for p in existing}
    still_needed = TARGET - len(existing)
    log.info("Need %d more stories to reach %d.", still_needed, TARGET)

    driver = make_driver()
    try:
        log.info("Step 1: Collecting URLs from all categories...")
        urls = collect_all_urls(driver)
        log.info("Total URLs found: %d", len(urls))

        # Filter out already scraped ones
        new_urls = [
            u for u in urls
            if u.rstrip("/").split("/")[-1].replace(".html", "") not in already_scraped_slugs
        ]
        log.info("New (unscraped) URLs: %d", len(new_urls))

        log.info("Step 2: Scraping new stories...")
        stories = []
        for url in tqdm(new_urls, desc="Scraping"):
            if len(stories) >= still_needed:
                break

            slug = url.rstrip("/").split("/")[-1].replace(".html", "")
            cache_path = OUTPUT_DIR / f"{slug}.json"

            story = extract_story(driver, url)
            if story:
                cache_path.write_text(
                    json.dumps(story, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                stories.append(story)
                log.info("  ✓ [%d/%d] %s", len(existing) + len(stories), TARGET, story["title"] or slug)
            else:
                log.warning("  ✗ Failed: %s", slug)

            time.sleep(1.2)

        # Step 3: Rebuild corpus.txt from ALL cached stories
        log.info("Step 3: Rebuilding corpus.txt from all cached stories...")
        all_stories = []
        for p in sorted(OUTPUT_DIR.glob("*.json")):
            try:
                all_stories.append(json.loads(p.read_text(encoding="utf-8")))
            except Exception:
                continue

        with OUTPUT_FILE.open("w", encoding="utf-8") as f:
            for s in all_stories:
                f.write(s["text"] + "\n")

        # Also save full stories.json
        Path("stories.json").write_text(
            json.dumps(all_stories, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        log.info("Done ✓  |  Total stories: %d  |  corpus.txt: %d bytes",
                 len(all_stories), OUTPUT_FILE.stat().st_size)

    finally:
        driver.quit()
        log.info("Browser closed.")


if __name__ == "__main__":
    main()