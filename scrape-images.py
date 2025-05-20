from icrawler.builtin import GoogleImageCrawler
import os
from pathlib import Path

category_keywords = {
    'front_bumper': [
        'front bumper damage car',
        'car front crash',
        'damaged front car view',
        'head-on car accident'
    ],
    'rear_bumper': [
        'rear bumper damage car',
        'rear end car crash',
        'car back accident damage'
    ],
    'windshield': [
        'cracked windshield car',
        'broken windshield car',
        'car front glass damage'
    ],
    'side_panel': [
        'side dented car',
        'side door damage car',
        'car side accident'
    ],
    'undamaged_car': [
        'new car front view',
        'car front without damage',
        'car dealership front photo'
    ]
}

base_dir = 'snaproute_dataset'
os.makedirs(base_dir, exist_ok=True)

MAX_IMAGES = 20

for category, keywords in category_keywords.items():
    save_dir = os.path.join(base_dir, category)
    os.makedirs(save_dir, exist_ok=True)

    downloaded = False

    for keyword in keywords:
        crawler = GoogleImageCrawler(storage={'root_dir': save_dir})
        crawler.crawl(keyword=keyword, max_num=MAX_IMAGES)

        image_count = len(list(Path(save_dir).glob("*.[jp][pn]g")))  # jpg or png

        if image_count >= MAX_IMAGES:
            downloaded = True
            break

