import re

def normalize_brand(title):
    """Extract and normalize brand name from title"""
    title = title.strip().lower()
    mappings = {
        'apple': 'Apple',
        'samsung': 'Samsung',
        'oneplus': 'OnePlus',
        'xiaomi': 'Xiaomi',
        'redmi': 'Xiaomi',
        'oppo': 'OPPO',
        'vivo': 'Vivo',
        'realme': 'Realme',
        'google': 'Google',
        'nothing': 'Nothing',
        'motorola': 'Motorola',
        'nokia': 'Nokia',
        'iqoo': 'iQOO',
        'lava': 'Lava',
        'zeno': 'Zeno',
        'acer': 'Acer',
        'honor': 'HONOR',
        'poco': 'POCO'
    }

    # Remove common wrappers
    title = re.sub(r'^\(?(refurbished|renewed|pre[-\s]?owned|used)\)?', '', title).strip()

    first_word = title.split()[0]
    return mappings.get(first_word, first_word.title())


def normalize_condition(condition):
    if not condition or not isinstance(condition, str):
        return 'Good'  
    condition = condition.strip().lower()
    if 'excellent' in condition or 'mint' in condition or 'like new' in condition:
        return 'Excellent'
    elif 'good' in condition or 'very good' in condition or 'great' in condition:
        return 'Good'
    elif 'fair' in condition or 'average' in condition or 'ok' in condition:
        return 'Fair'
    elif 'poor' in condition or 'damaged' in condition:
        return 'Poor'
    elif "refurbished" in condition or 'Renewed' in condition:
        return "Refurbished"
    else:
        return condition.capitalize()


def extract_model(device_name: str) -> str:
    device_name = re.sub(r'\b(Refurbished|Renewed|Pre[-\s]?Owned|Used)\b', '', device_name, flags=re.IGNORECASE)

    # Remove any leading parentheses/brackets/tags
    device_name = re.sub(r'^\s*\(.*?\)\s*', '', device_name)

    # Remove known brands
    brand_keywords = [
        r'Apple', r'Samsung', r'OnePlus', r'Xiaomi', r'Redmi', r'OPPO',
        r'Vivo', r'Realme', r'Google', r'Motorola', r'Nokia', r'Nothing',
        r'iQOO', r'Lava', r'Zeno', r'Acer', r'Honor', r'POCO'
    ]
    pattern = r'^(' + '|'.join(brand_keywords) + r')\s+'
    device_name = re.sub(pattern, '', device_name, flags=re.IGNORECASE)

    # Clean up whitespaces and stray punctuation
    device_name = re.sub(r'\s*\(\s*', ' (', device_name)
    device_name = re.sub(r'\s*\)\s*', ')', device_name)
    device_name = re.sub(r'\s+', ' ', device_name)
    device_name = device_name.strip(' -')

    return device_name.strip()
