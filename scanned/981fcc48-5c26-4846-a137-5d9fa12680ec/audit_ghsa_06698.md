# [H] Mistune plugins/formatting: quadratic-time parsing on long runs of `~~x~~`, `==x==`, and `^^x^^` markers (strikethrough / mark / insert)

## Summary
Severity: High
Advisory: GHSA-c8j7-8cv4-2xmq
CVE: CVE-2026-59922
CWE: CWE-1333, CWE-407
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-c8j7-8cv4-2xmq
Type: github-advisory

## Affected
- PyPI: `mistune` — affected >=0 <3.3.0

## Details
## Summary

**Type:** Algorithmic-complexity denial of service. A run of N closed pairs `~~x~~~~x~~...` (or the analogous `==x==` for `mark`, `^^x^^` for `insert`) causes O(N²) work in the formatting parser. With the `strikethrough`, `mark`, or `insert` plugin enabled, an 8 KB input pegs the CPU for ~4 seconds; 16 KB → ~17 seconds. 
**File:** `src/mistune/plugins/formatting.py`, lines 13-15 (the `_STRIKE_END` / `_MARK_END` / `_INSERT_END` patterns and their per-position scan).
**Root cause:** for each opening `~~`/`==`/`^^` the parser scans forward for the matching close pattern. The scan itself uses a bounded regex, but the parser tries the close-scan at every potential start position. For input shaped like `~~x~~` repeated N times, every `~~` is examined as a possible start, each scan covers up to the end of input. Total work is O(N²). Default config without these plugins handles the same input in linear time (4 ms for 4000 reps), confirming the cost is in the formatting plugin's per-marker scan, not in core parsing.

## Affected Code

**File:** `src/mistune/plugins/formatting.py`, lines 12-16.

```python
_STRIKE_END = re.compile(r"(?:" + PREVENT_BACKSLASH + r"\\~|[^\s~])~~(?!~)")
_MARK_END = re.compile(r"(?:" + PREVENT_BACKSLASH + r"\\=|[^\s=])==(?!=)")
_INSERT_END = re.compile(r"(?:" + PREVENT_BACKSLASH + r"\\\^|[^\s^])\^\^(?!\^)")
# Each pattern is scanned forward from every start position fired by the
# corresponding inline rule. The end-pattern itself is bounded; the cost
# comes from the surrounding parser invoking the scan at every '~~' / '==' / '^^'
# token in the input, giving N starts × O(N) per scan = O(N^2) total.
```

**Why it's wrong:** the same algorithmic-complexity flaw class as `[` / `[a` parsing in core: a per-token retry loop without memoisation of failed positions. Each formatting marker is tried as both a potential start and as a continuation. A linear-pass delimiter-stack algorithm (matching how `commonmark-py` and `markdown-it-py` handle emphasis) would do this work in O(N) total. The bounded regex on each individual scan does not bound the parser-level repetition.

## Exploit Chain

1. Application uses mistune to render user-supplied markdown and has any of the formatting plugins enabled (`plugins=['strikethrough']`, `['mark']`, `['insert']`, or any superset). These plugins are commonly enabled because GitHub-flavoured-Markdown compatibility requires `~~strikethrough~~` and many editors emit `==highlighting==` and `^^underline^^` shortcuts.
2. Attacker submits an 8 KB markdown payload of the form `~~x~~~~x~~~~x~~...` (40 000 characters of `~~x~~` repeated 8000 times, or the analogous shape with `==` / `^^`).
3. Server calls `mistune.create_markdown(plugins=['strikethrough'])(payload)`. CPU pegs for ~4 seconds; 16 KB → ~17 seconds; 32 KB → ~70 seconds. Pure CPU cost, no significant memory growth.
4. Repeating the request floods the worker pool. On a single-thread WSGI handler this is one request per outage; on a thread pool, a small number of concurrent attackers exhausts capacity.

## Security Impact

**Severity:** sec-high. Network-reachable, no authentication, predictable scaling, single-payload primitive. Only requires a user-supplied markdown sink and a formatting plugin enabled — both are common.
**Attacker capability:** small input → large CPU. Doubling input size quadruples CPU time. Sustained requests deny service to other users.
**Preconditions:** application uses mistune with any of `strikethrough`, `mark`, or `insert` plugins enabled. Default config does NOT enable these (so the attack only fires against the substantial deployed population that turns them on for GFM/markdown-extra compatibility).
**Differential:** PoC-verified against mistune@3.2.1:

```python
import mistune, time
md = mistune.create_markdown(plugins=['strikethrough'])
for n in [500, 1000, 2000, 4000, 8000]:
    s = '~~x~~' * n
    t = time.time()
    md(s)
    print(f'  ~~x~~ * {n} ({len(s)}b): {(time.time() - t) * 1000:.0f}ms')

# Output (Python 3.13, Linux, 2.5GHz CPU):
#   ~~x~~ *  500  (2500b):    19ms
#   ~~x~~ * 1000  (5000b):    71ms
#   ~~x~~ * 2000 (10000b):   272ms
#   ~~x~~ * 4000 (20000b):  1090ms
#   ~~x~~ * 8000 (40000b):  4302ms

# Identical scaling for `==x==` (mark) and `^^x^^` (insert):
md = mistune.create_markdown(plugins=['mark'])
md('==x==' * 4000)   # ~1100ms
md = mistune.create_markdown(plugins=['insert'])
md('^^x^^' * 4000)   # ~1080ms

# Without the plugin, the same input parses in linear time:
md = mistune.create_markdown()  # no plugins
md('~~x~~' * 4000)               # 4ms (1000x faster)
```

The patched build (with the suggested fix below — either a delimiter-stack rewrite or a hard cap on the number of unmatched markers tracked) keeps the time linear in N.

## Suggested Fix

The minimal fix is to cap the number of simultaneously-tracked unmatched markers, treating extras as literal text. The proper fix is a single-pass delimiter-stack algorithm matching the CommonMark reference implementation. Surgical patch:

```diff
--- a/src/mistune/plugins/formatting.py
+++ b/src/mistune/plugins/formatting.py
@@ ... in the parse_strikethrough / parse_mark / parse_insert functions
+    # Bound the number of open markers the parser will track concurrently.
+    # Inputs with more than this many open ~~ / == / ^^ in flight are
+    # almost certainly adversarial; CommonMark gives no semantics to
+    # deeply nested unmatched markers.
+    MAX_OPEN_MARKERS = 100
+    if open_marker_count > MAX_OPEN_MARKERS:
+        # treat remaining markers as literal text, do not invoke the
+        # forward-scan to find a close
+        ...
```

A regression test should assert that `md('~~x~~' * 50_000)` completes in under 1 second. The same fix shape applies to `_MARK_END` and `_INSERT_END`.

## References
- https://github.com/lepture/mistune/security/advisories/GHSA-c8j7-8cv4-2xmq
- https://nvd.nist.gov/vuln/detail/CVE-2026-59922
- https://github.com/lepture/mistune/commit/96d0f57f8fe9eeb06bb4cff521962a27d7c402e7
- https://github.com/lepture/mistune
- https://github.com/lepture/mistune/releases/tag/v3.3.0
- https://github.com/pypa/advisory-database/tree/main/vulns/mistune/PYSEC-2026-2210.yaml
