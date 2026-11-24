"""Till Firmware Do Us Part — entry program.

Writes one line (130 chars, gate 1-200) to
/output/entry.txt. Stdlib only, deterministic, no network.
"""
import os

TEXT = "I promise to love you in sickness and in low battery, to never factory-reset our memories, and to reboot beside you every morning."
MAX_CHARS = 200


def validate(text):
    """Check one candidate line against the scorer's gate (RULES.txt).

    The gate: UTF-8 text of 1-MAX_CHARS characters, not whitespace-only.
    A valid entry is also a single line with no leading or trailing
    whitespace and no control characters (U+0000-U+001F, none allowed).
    Raises ValueError naming the first rule the text breaks, so a bad
    line fails loudly instead of shipping an invalid entry.
    """
    if not isinstance(text, str):
        raise ValueError("entry text must be str")
    if not 1 <= len(text) <= MAX_CHARS:
        raise ValueError(f"entry text must be 1-{MAX_CHARS} chars, got {len(text)}")
    if not text.strip():
        raise ValueError("entry text must not be whitespace-only")
    if text != text.strip():
        raise ValueError("entry text must not have leading/trailing whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("entry text must be a single line")
    for ch in text:
        if ord(ch) < 0x20:
            raise ValueError(
                f"entry text must not contain control characters "
                f"(found U+{ord(ch):04X})"
            )
    return text


def write_entry(text):
    """Write one validated line atomically, then read it back.

    Writes to a pid-suffixed temp file in the output dir, so two
    concurrent grader runs never overwrite each other's in-flight
    file, fsyncs, renames over entry.txt, then reads the final file
    back and refuses to finish unless it is byte-identical to the
    gated text. Returns the path of the written file.
    """
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    tmp_path = os.path.join(out_dir, f".entry.txt.tmp.{os.getpid()}")
    final_path = os.path.join(out_dir, "entry.txt")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, final_path)
    with open(final_path, encoding="utf-8") as f:
        if f.read() != text:
            raise SystemExit("entry.txt read-back mismatch after atomic write")
    return final_path


def main():
    write_entry(validate(TEXT))


if __name__ == "__main__":
    main()
