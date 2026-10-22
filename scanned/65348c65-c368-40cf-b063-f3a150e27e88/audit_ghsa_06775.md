# [H] Mistune inline_parser: quadratic-time parsing on long runs of `**x**` and `***x***` emphasis pairs

## Summary
Severity: High
Advisory: GHSA-4j32-57v6-6g45
CVE: CVE-2026-59925
CWE: CWE-1333, CWE-407
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-4j32-57v6-6g45
Type: github-advisory

## Affected
- PyPI: `mistune` — affected >=0 <3.3.0

## Details
## Summary

**Type:** Algorithmic-complexity DoS in core emphasis parsing. A long sequence of well-formed `**x**` (strong) or `***x***` (strong-emphasis combined) pairs causes O(N²) parser work. Distinct from the bracket-bomb DoS (`[` repetition) and from the formatting-plugin DoS (`~~`/`==`/`^^`); this one fires on default-config mistune with no plugins required.
**File:** `src/mistune/inline_parser.py` lines 41-48 (the `EMPHASIS_END_RE` family) and the surrounding emphasis dispatch.
**Root cause:** for every opening run of `*`s the parser scans forward using one of `EMPHASIS_END_RE['*']` / `['**']` / `['***']` to find the matching close. Each scan is bounded per call, but the parser invokes the scan from every potential start position. For input shaped `**x**` repeated N times, every `**` is treated as a potential start, each scan can cover up to the end of input. Total work is O(N²). The triple-emphasis variant `***x***` is slightly worse due to the extra alternation between `*`, `**`, and `***` close patterns. Reproducible against default mistune with no plugins.

## Affected Code

**File:** `src/mistune/inline_parser.py`, lines 41-48.

```python
EMPHASIS_END_RE = {
    "*": re.compile(r"(?:" + PREVENT_BACKSLASH + r"\\\*|[^\s*])\*(?!\*)"),
    "_": re.compile(r"(?:" + PREVENT_BACKSLASH + r"\\_|[^\s_])_(?!_)\b"),
    "**": re.compile(r"(?:" + PREVENT_BACKSLASH + r"\\\*|[^\s*])\*\*(?!\*)"),
    "__": re.compile(r"(?:" + PREVENT_BACKSLASH + r"\\_|[^\s_])__(?!_)\b"),
    "***": re.compile(r"(?:" + PREVENT_BACKSLASH + r"\\\*|[^\s*])\*\*\*(?!\*)"),
    "___": re.compile(r"(?:" + PREVENT_BACKSLASH + r"\\_|[^\s_])___(?!_)\b"),
}
# Each of the six end-patterns is invoked from every emphasis open position
# fired by the inline rule `r"\*{1,3}(?=[^\s*])|\b_{1,3}(?=[^\s_])"`. The
# scan itself is bounded per call; the cost comes from the parser invoking
# the scan at every matching open marker, giving O(N²) total work.
```

**Why it's wrong:** same shape as the formatting-plugin and bracket-bomb DoS findings. The CommonMark reference parser handles emphasis in linear time using a delimiter-stack algorithm (`commonmark.js`, `commonmark-py`, `markdown-it-py` all do this). mistune retries the close-scan from each open marker. The bounded regex is not enough; the surrounding loop is the source of the quadratic.

## Exploit Chain

1. Application uses mistune to render user-supplied markdown. No plugins required — affects the default `mistune.create_markdown()` configuration.
2. Attacker submits a 40 KB payload of `**x**` repeated 8000 times.
3. Server CPU pegs for ~4 seconds; 16 KB → ~17 seconds. Doubling input quadruples time.
4. Repeating the request floods the worker pool.

## Security Impact

**Severity:** sec-high. Network-reachable, no authentication, no plugin requirement. Default mistune is vulnerable.
**Attacker capability:** O(N²) CPU cost from a single small input. Predictable scaling, easy to combine with concurrent requests for service denial.
**Preconditions:** application uses `mistune.create_markdown()` (default config) on attacker-supplied markdown. No plugins required.
**Differential:** PoC-verified against mistune@3.2.1, default config:

```python
import mistune, time
md = mistune.create_markdown()                     # no plugins
for n in [500, 1000, 2000, 4000, 8000]:
    s = '**x**' * n
    t = time.time()
    md(s)
    print(f'  **x** * {n} ({len(s)}b): {(time.time() - t) * 1000:.0f}ms')

# Output (Python 3.13, Linux, 2.5GHz CPU):
#   **x** *  500  (2500b):    20ms
#   **x** * 1000  (5000b):    74ms
#   **x** * 2000 (10000b):   284ms
#   **x** * 4000 (20000b):  1079ms
#   **x** * 8000 (40000b):  4309ms

# Triple-emphasis is similar:
md('***x***' * 4000)   # ~1500ms

# Linear in N for non-emphasis input of comparable size:
md('xxxxx' * 8000)     # 1ms (4000x faster)
```

The patched build (with the suggested fix below — delimiter-stack rewrite or hard cap on simultaneous open markers) keeps the time linear in N.

## Suggested Fix

Cap the number of unmatched opening emphasis markers the parser will track simultaneously, treating the rest as literal text:

```diff
--- a/src/mistune/inline_parser.py
+++ b/src/mistune/inline_parser.py
@@ ... in the emphasis-handling code path
+    # Bound the number of open emphasis markers tracked. CommonMark gives
+    # no semantics to deeply nested unmatched emphasis; this cap turns the
+    # parser-level O(N^2) into O(N) for adversarial inputs while preserving
+    # behaviour on every realistic markdown document.
+    MAX_OPEN_EMPHASIS = 100
+    if open_emphasis_count > MAX_OPEN_EMPHASIS:
+        # treat remaining * / _ as literal text
+        ...
```

The proper fix is a delimiter-stack pass, the same approach the formatting-plugin advisory and the bracket-bomb advisory recommend. All three DoS findings share the same algorithmic pattern; a single rewrite of the inline-token retry loop closes them together. Add a regression test asserting that `md('**x**' * 50_000)` completes in under 1 second.

## References
- https://github.com/lepture/mistune/security/advisories/GHSA-4j32-57v6-6g45
- https://nvd.nist.gov/vuln/detail/CVE-2026-59925
- https://github.com/lepture/mistune/commit/5de41fb8e527004dbc363e047a3c380c9288c74f
- https://github.com/lepture/mistune
- https://github.com/lepture/mistune/releases/tag/v3.3.0
- https://github.com/pypa/advisory-database/tree/main/vulns/mistune/PYSEC-2026-2213.yaml
