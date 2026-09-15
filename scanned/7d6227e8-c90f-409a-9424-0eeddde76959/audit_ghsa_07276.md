# [M] Open WebUI: ReDoS in skill-mention regexes causes whole-instance DoS on default config

## Summary
Severity: Medium
Advisory: GHSA-ffpj-xv5c-p3gw
CVE: CVE-2026-59220
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-ffpj-xv5c-p3gw
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0.9.2 <0.10.0

## Details
## Summary
Two regexes in `backend/open_webui/utils/middleware.py` that parse `<$skillId|label>` skill-mention tags backtrack in O(n²) on input that contains `<$` followed by a long run with no closing `>`. Both run synchronously, on the asyncio event loop, on **every** chat completion with no feature gate. Because the default deployment is a single uvicorn worker, one such input pins a CPU core inside `re` and freezes the entire instance for all users until the worker is killed. Any authenticated user can trigger it with one chat message; it also fires accidentally on benign retrieved content (a RAG chunk or tool output) containing the pattern.

## Affected versions
`>= 0.9.2, < 0.10.0`. Fixed in **v0.10.0** (there is no 0.9.7 release).
- `SKILL_MENTION_RE` (the extract pattern) has been O(n²) since **v0.9.2**; exploitable on 0.9.2–0.9.5 with a large input (hundreds of KB).
- **v0.9.6** added a second, far more aggressive O(n²) in the strip pattern (introduced by the "keep label as readable text" change), so on 0.9.6 a small input is enough to hang the instance.

Both are fixed by the same patch.

## Affected component
`backend/open_webui/utils/middleware.py` (line numbers as of v0.9.6):

```python
# line 2223 — used by extract_skill_ids_from_messages(), called unconditionally (~line 2625)
SKILL_MENTION_RE = re.compile(r'<\$([^|>]+)\|?[^>]*>')

# line 2247 — used by strip_skill_mentions(), called unconditionally (line 2662)
strip_re = re.compile(r'<\$[^|>]+\|?([^>]*)>')
```

`extract_skill_ids_from_messages()` runs before the `if all_skill_ids:` block (that guard gates only skill *injection*, not the regex), and `strip_skill_mentions()` runs with no guard at all. Neither requires a skill to exist or any setting to be enabled. Both functions are plain synchronous calls inside the async `process_chat_payload` coroutine, so they block the event loop; with the default `UVICORN_WORKERS=1` (`backend/start.sh`) the whole instance stalls.

## Root cause
`[^|>]` is a subset of `[^>]`, so the quantifier pair `[^|>]+ \|? [^>]*` is ambiguous: on input that never closes with `>`, `[^|>]+` greedily consumes the tail, `>` fails, and the engine backtracks through every split point between `[^|>]+` and `[^>]*` — O(n) positions each doing O(n) work. Polynomial, not exponential, but more than enough to hang a single worker on a ~100 KB input.

## Proof of concept
Standalone (no Open WebUI required):

```python
import re, time
EXTRACT = re.compile(r'<\$([^|>]+)\|?[^>]*>')
STRIP   = re.compile(r'<\$[^|>]+\|?([^>]*)>')
for n in (8_000, 16_000, 32_000, 64_000):
    s = '<$' + ('a' * n)
    for name, rx in (('extract', EXTRACT), ('strip', STRIP)):
        t = time.perf_counter(); rx.search(s)
        print(f'n={n:>6} {name:>7} = {(time.perf_counter()-t)*1000:8.1f} ms')
```

Time quadruples per doubling of `n` (textbook O(n²)); the strip pattern runs for ~6 seconds on a 64k blob and for minutes on a ~96 KB one.

End-to-end against a live instance (default config):
1. `docker run ghcr.io/open-webui/open-webui:v0.9.6` on defaults.
2. Log in as any user (no admin or skill setup).
3. Send a chat message containing `<$` followed by 50k+ characters with no `>`.
4. One CPU core pegs in `re`; UI and API stop responding for every user until the worker is killed.

## Patch
Rewrite the optional `|label` as a non-capturing optional group so the two quantifiers no longer overlap. Both patterns become linear; captures and substituted output are unchanged on well-formed `<$id|label>`, `<$id|>`, and bare `<$id>` mentions.

```python
SKILL_MENTION_RE = re.compile(r'<\$([^|>]+)(?:\|[^>]*)?>')
strip_re         = re.compile(r'<\$[^|>]+(?:\|([^>]*))?>')
```

After the patch the same hostile input returns in under 1 ms. Shipped in v0.10.0.

## Credit
Reported by @Vlad-WKG, including a correct root-cause analysis and patch.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-ffpj-xv5c-p3gw
- https://nvd.nist.gov/vuln/detail/CVE-2026-59220
- https://github.com/open-webui/open-webui/commit/61a26722155ec6ee1b629cf8dfcf975098c18331
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.10.0
