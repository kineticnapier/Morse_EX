from morse_dict import *
from helper_func import *


def preprocess_text(text: str, mode: str) -> str:
    if mode == "jp":
        return normalize_japanese_text(text)
    return text


def _encode_en_char(ch: str) -> tuple[list[str], bool]:
    lower = ch.lower()
    if lower in EN_MORSE:
        return [EN_MORSE[lower]], False
    return [f"[{ch}]"], True


def _encode_jp_char(ch: str) -> tuple[list[str], bool]:
    lower = ch.lower()

    if ch in REVERSE_DAKUTEN:
        base = REVERSE_DAKUTEN[ch]
        return [JP_MORSE[base], DAKUTEN], False

    if ch in REVERSE_HANDAKUTEN:
        base = REVERSE_HANDAKUTEN[ch]
        return [JP_MORSE[base], HANDAKUTEN], False

    if ch in JP_MORSE:
        return [JP_MORSE[ch]], False

    if lower in EN_MORSE:
        return [EN_MORSE[lower]], False

    return [f"[{ch}]"], True


def text_to_morse(text: str, mode: str) -> tuple[str, bool]:
    text = preprocess_text(text, mode)

    encoder = _encode_en_char if mode == "en" else _encode_jp_char

    out: list[str] = []
    err_flag = False

    for ch in text:
        codes, has_error = encoder(ch)
        out.extend(codes)
        err_flag |= has_error

    return " ".join(out), err_flag


def _decode_jp_token(token: str) -> str | None:
    return REV_JP_MORSE.get(token)


def _decode_en_token(token: str) -> str | None:
    return REV_EN_MORSE.get(token)


def _apply_japanese_marks(
    base_char: str,
    tokens: list[str],
    index: int,
) -> tuple[str, int]:
    if index + 1 >= len(tokens):
        return base_char, index

    next_token = tokens[index + 1]

    if next_token == DAKUTEN and base_char in DAKUTEN_MAP:
        return DAKUTEN_MAP[base_char], index + 1

    if next_token == HANDAKUTEN and base_char in HANDAKUTEN_MAP:
        return HANDAKUTEN_MAP[base_char], index + 1

    return base_char, index


def morse_to_text(morse: str, mode: str) -> tuple[str, bool]:
    tokens = morse.strip().split()
    out: list[str] = []
    err_flag = False
    i = 0

    while i < len(tokens):
        token = tokens[i]

        if token == "/":
            out.append(" ")
            i += 1
            continue

        if mode == "en":
            char = _decode_en_token(token)
            if char is None:
                out.append(f"[{token}]")
                err_flag = True
            else:
                out.append(char)
            i += 1
            continue

        # jp モード: 和文優先、だめなら英文
        char = _decode_jp_token(token)
        if char is not None:
            char, i = _apply_japanese_marks(char, tokens, i)
            out.append(char)
            i += 1
            continue

        char = _decode_en_token(token)
        if char is not None:
            out.append(char)
            i += 1
            continue

        out.append(f"[{token}]")
        err_flag = True
        i += 1

    return "".join(out), err_flag