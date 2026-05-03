import random
import os

last_sentence = ""

def load_data():
    """Đọc dữ liệu từ data/sentences.txt theo định dạng level|content"""
    data_dict = {"easy": [], "medium": [], "hard": []}
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", "sentences.txt")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "|" in line:
                    level, content = line.split('|', 1)
                    level = level.lower().strip()
                    if level in data_dict:
                        data_dict[level].append(content.strip())
    except FileNotFoundError:
        data_dict["easy"] = ["hello world", "python is fun"]
        
    return data_dict

def get_challenge(data_dict, level, mode="sentence"):
    """Xử lý chọn level và random câu không trùng lặp"""
    global last_sentence
    
    pool = data_dict.get(level.lower(), data_dict["easy"])
    if not pool:
        return "Danh sách câu hỏi trống!"

    if mode == "paragraph":
        selected = random.sample(pool, min(3, len(pool)))
        return " ".join(selected)
    
    choice = random.choice(pool)
    while choice == last_sentence and len(pool) > 1:
        choice = random.choice(pool)
        
    last_sentence = choice
    return choice
