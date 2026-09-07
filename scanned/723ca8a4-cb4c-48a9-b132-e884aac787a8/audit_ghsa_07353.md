# [M] Mistune renderers/html.safe_url: HARMFUL_PROTOCOLS list misses legacy and chained schemes that historically chain to `javascript:` execution

## Summary
Severity: Medium
Advisory: GHSA-qfrw-5rxm-mhh2
CVE: CVE-2026-59929
CWE: CWE-184, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-qfrw-5rxm-mhh2
Type: github-advisory

## Affected
- PyPI: `mistune` — affected >=0 <3.3.0

## Details
## Summary

**Type:** URL-scheme allowlist gap. The `safe_url` filter only blocks the four schemes `javascript:`, `vbscript:`, `file:`, `data:`. Several other schemes are accepted into rendered `<a href="...">` and `<img src="...">` tags despite being known XSS vectors in legacy or chain-handling browsers. The same gap applies to direct links, reference links, and autolinks.
**File:** `src/mistune/renderers/html.py`, line 11-23 (HARMFUL_PROTOCOLS list).
**Root cause:** the HARMFUL_PROTOCOLS tuple is a hardcoded, opt-out denylist of four entries. Browsers historically supported (and some still partially support) several other schemes that either execute JavaScript directly (`livescript:`, `mocha:`) or wrap a `javascript:` payload (`feed:javascript:`, `view-source:javascript:`, `jar:javascript:`, `ms-its:javascript:`, `mk:@MSITStore:javascript:`). On user-agents that still recognise these schemes (older Firefox builds for `feed:`/`jar:`, all Internet Explorer / Edge Legacy for `ms-its:`/`mk:`/`res:`, niche chrome-style browsers, browser extensions that register custom protocol handlers), clicking a link rendered by mistune executes attacker-controlled JavaScript in the page's origin.

## Affected Code

**File:** `src/mistune/renderers/html.py`, lines 10-62.

```python
class HTMLRenderer(BaseRenderer):
    HARMFUL_PROTOCOLS: ClassVar[Tuple[str, ...]] = (
        "javascript:",
        "vbscript:",
        "file:",
        "data:",
    )                                                         # <-- BUG: incomplete denylist
    GOOD_DATA_PROTOCOLS: ClassVar[Tuple[str, ...]] = (
        "data:image/gif;",
        "data:image/png;",
        "data:image/jpeg;",
        "data:image/webp;",
    )

    def safe_url(self, url: str) -> str:
        if self._allow_harmful_protocols is True:
            return escape_text(url)
        _url = url.lower()
        if self._allow_harmful_protocols and _url.startswith(tuple(self._allow_harmful_protocols)):
            return escape_text(url)
        if _url.startswith(self.HARMFUL_PROTOCOLS) and not _url.startswith(self.GOOD_DATA_PROTOCOLS):
            return "#harmful-link"
        return escape_text(url)                               # <-- BUG: any scheme not in HARMFUL_PROTOCOLS passes through
```

**Why it's wrong:** an opt-out denylist for URL schemes is the wrong shape. The set of schemes a user-agent might honour is unbounded (registered handlers, browser extensions, OS-level protocol registrations, custom intent handlers on Android, etc.), but the set of schemes a markdown renderer needs to allow is small (`http://`, `https://`, `mailto:`, optionally `tel:`, `ftp:`, fragment-only `#anchor`, and a few image-only `data:` types). Switching to an opt-in allowlist with a `safe_extra_protocols` knob for callers who need others would close every variant of this bug class permanently. The current code accepts every chained-scheme XSS vector for as long as the project remembers to keep the denylist current.

## Exploit Chain

1. Application accepts attacker-supplied markdown and renders it with mistune. The default `escape=True` prevents raw HTML, but link href/image src filtering is the only XSS defense for `[click](...)` and `![alt](...)` syntax.
2. Attacker writes `[click here](feed:javascript:alert(document.cookie))`. mistune's `safe_url` checks `feed:javascript:alert(document.cookie)` against `HARMFUL_PROTOCOLS = ('javascript:', 'vbscript:', 'file:', 'data:')` — none match. The href is escape_text'd (HTML-entity escape) and emitted as `<a href="feed:javascript:alert(document.cookie)">click here</a>`.
3. Victim using a Firefox build that still has the feed handler registered (extension, configuration, or LTS that retained the feed reader past the 64.0 removal — including some forks and ESR builds) clicks the link. Firefox's feed handler invokes the inner URL, which is `javascript:alert(...)`. JS executes in the page's origin. Victim's session cookie is exfiltrated.
4. Same pattern for `livescript:alert(1)` (Netscape Communicator era, still recognised by some niche browsers / browser-emulator tools), `view-source:javascript:alert(1)` (Firefox, see CVE-2009-1938), `jar:javascript:alert(1)` (older Firefox), `ms-its:javascript:` (IE/Edge Legacy), `res:javascript:` (IE), `mk:@MSITStore:javascript:` (IE CHM viewer). Each user-agent that recognises one of these is exploitable; the user-agent population that recognises at least one is not negligible (corporate environments still running Edge Legacy compatibility mode, locked-down kiosk browsers, Android WebView in apps that register custom intent handlers, Linux distros with old Firefox ESR plus the `feed:` extension, etc.).

The same primitive applies to image src (`![](feed:javascript:...)` rendered as `<img src="feed:...">`) — though most browsers don't fetch javascript: from img src, the same chained handler quirk applies on a few user-agents — and to reference links and autolinks (verified in the PoC below; the rendered HTML is identical regardless of which markdown link syntax is used).

## Security Impact

**Severity:** sec-moderate. Conditional XSS depending on user-agent. Modern Chrome / Edge Chromium / Safari ignore most of these schemes, but Firefox forks, Edge Legacy, in-app WebViews, browser extensions registering custom handlers, and corporate browser deployments are exposed. Defence-in-depth is the framing: a markdown renderer should not need to track which browsers still honour which legacy chained-scheme.
**Attacker capability:** plant a link in any place the application renders user-supplied markdown. When clicked by a user-agent that honours the legacy scheme, the attacker's JavaScript runs in the page's origin (steal cookies, perform actions as the victim, etc.).
**Preconditions:** application uses mistune to render attacker-influenced markdown. Default config. Victim user-agent is one of the affected populations. No specific mistune option is required.
**Differential:** PoC-verified against mistune@3.2.1, default config. The following inputs all PASS the filter and reach the rendered HTML unchanged:

```python
import mistune
md = mistune.create_markdown()
for url in [
    'feed:javascript:alert(1)',                  # Firefox feed handler chain
    'livescript:alert(1)',                       # Netscape, niche browsers
    'mocha:alert(1)',                            # Netscape, niche browsers
    'view-source:javascript:alert(1)',           # Firefox view-source chain (CVE-2009-1938 class)
    'jar:javascript:alert(1)',                   # Firefox jar: handler chain
    'ms-its:javascript:alert(1)',                # IE/Edge Legacy InfoTech Storage handler
    'mk:@MSITStore:javascript:alert(1)',         # IE CHM viewer chain
    'res:javascript:',                           # IE resource: handler
]:
    print(md(f'[click]({url})').strip())

# Output (each one passes the filter):
#   <p><a href="feed:javascript:alert(1)">click</a></p>
#   <p><a href="livescript:alert(1)">click</a></p>
#   <p><a href="mocha:alert(1)">click</a></p>
#   <p><a href="view-source:javascript:alert(1)">click</a></p>
#   <p><a href="jar:javascript:alert(1)">click</a></p>
#   <p><a href="ms-its:javascript:alert(1)">click</a></p>
#   <p><a href="mk:@MSITStore:javascript:">click</a></p>
#   <p><a href="res:javascript:">click</a></p>
```

For comparison, the four schemes already in the denylist are correctly blocked: `javascript:`, `vbscript:`, `file:`, `data:text/html` all return `<a href="#harmful-link">`.

The same gap applies to reference links (`[click][ref]\n\n[ref]: feed:javascript:alert(1)` → `<a href="feed:javascript:alert(1)">`) and to autolinks (`<feed:javascript:alert(1)>` → `<a href="feed:javascript:alert(1)">`).

## Suggested Fix

Switch from denylist to allowlist. The set of schemes a markdown renderer needs to allow is small and well-known; the set of schemes that might trigger handler chains is unbounded.

```diff
--- a/src/mistune/renderers/html.py
+++ b/src/mistune/renderers/html.py
@@ -7,21 +7,28 @@ class HTMLRenderer(BaseRenderer):

     _escape: bool
     NAME: ClassVar[Literal["html"]] = "html"
-    HARMFUL_PROTOCOLS: ClassVar[Tuple[str, ...]] = (
-        "javascript:",
-        "vbscript:",
-        "file:",
-        "data:",
-    )
+    SAFE_PROTOCOLS: ClassVar[Tuple[str, ...]] = (
+        "http:",
+        "https:",
+        "mailto:",
+        "tel:",
+        "ftp:",
+        "ftps:",
+        "irc:",
+        "ircs:",
+    )
     GOOD_DATA_PROTOCOLS: ClassVar[Tuple[str, ...]] = (
         "data:image/gif;",
         "data:image/png;",
         "data:image/jpeg;",
         "data:image/webp;",
     )

@@ -49,15 +56,21 @@ class HTMLRenderer(BaseRenderer):
     def safe_url(self, url: str) -> str:
-        if self._allow_harmful_protocols is True:
-            return escape_text(url)
-
-        _url = url.lower()
-        if self._allow_harmful_protocols and _url.startswith(tuple(self._allow_harmful_protocols)):
-            return escape_text(url)
-
-        if _url.startswith(self.HARMFUL_PROTOCOLS) and not _url.startswith(self.GOOD_DATA_PROTOCOLS):
-            return "#harmful-link"
-        return escape_text(url)
+        # Allow-list: only schemes in SAFE_PROTOCOLS, image-only data: URLs in
+        # GOOD_DATA_PROTOCOLS, scheme-relative URLs (//host/path), absolute
+        # paths (/path), and anchor-only references (#fragment) reach the
+        # rendered output. Everything else is replaced with '#harmful-link'.
+        if self._allow_harmful_protocols is True:
+            return escape_text(url)
+        _url = url.lower().lstrip()
+        if (
+            _url.startswith(self.SAFE_PROTOCOLS)
+            or _url.startswith(self.GOOD_DATA_PROTOCOLS)
+            or _url.startswith(("/", "#", "?"))
+            or ":" not in _url.split("/", 1)[0]   # bare relative path
+        ):
+            return escape_text(url)
+        if self._allow_harmful_protocols and _url.startswith(tuple(self._allow_harmful_protocols)):
+            return escape_text(url)
+        return "#harmful-link"
```

The `allow_harmful_protocols` option is preserved, so callers who genuinely want to allow a custom scheme can still opt in. The `lower().lstrip()` also closes the leading-whitespace evasion sub-case (e.g., ` javascript:` is already blocked by the current code via `lower().startswith`, but the same pattern needs to apply on the new allowlist branch). Add regression tests for each scheme listed in the PoC above asserting they resolve to `#harmful-link`.

## References
- https://github.com/lepture/mistune/security/advisories/GHSA-qfrw-5rxm-mhh2
- https://nvd.nist.gov/vuln/detail/CVE-2026-59929
- https://github.com/lepture/mistune/commit/c7101fcbb6e8790e8e39157c5ca2238fc6dd6cbc
- https://github.com/lepture/mistune
- https://github.com/lepture/mistune/releases/tag/v3.3.0
- https://github.com/pypa/advisory-database/tree/main/vulns/mistune/PYSEC-2026-2217.yaml
