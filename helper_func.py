from pykakasi import kakasi

def katakana_to_hiragana(text: str) -> str:
    result = []
    for ch in text:
        code = ord(ch)
        if 0x30A1 <= code <= 0x30F6:
            result.append(chr(code - 0x60))
        else:
            result.append(ch)
    return "".join(result)

def normalize_japanese_text(text: str) -> str:
    kks = kakasi()
    converted = kks.convert(text)
    reading = "".join(item.get("kana") or item.get("orig", "") for item in converted)
    reading = katakana_to_hiragana(reading)
    reading = reading.replace("ー", "")
    return reading