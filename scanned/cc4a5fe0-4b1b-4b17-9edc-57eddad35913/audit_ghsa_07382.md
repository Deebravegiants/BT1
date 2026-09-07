# [M] Jodit has cross-site scripting (XSS) via <script> nested in SVG that bypasses clean-html sanitization

## Summary
Severity: Medium
Advisory: GHSA-45qg-252v-3f7p
CVE: CVE-2026-65841
CWE: CWE-80
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-45qg-252v-3f7p
Type: github-advisory

## Affected
- npm: `jodit` — affected >=0 <4.13.6

## Details
A `<script>` element placed directly inside an `<svg>` (or MathML) container was not removed by Jodit's clean-html sanitizer.

The deny/allow tag filter compared `node.nodeName` against an upper-cased tag hash, but foreign (SVG/MathML) elements preserve their original-case node names — an SVG script reports `"script"`, not `"SCRIPT"` — so the default `denyTags` list (which includes `script`) did not match it. The script therefore survived in the editor value and serialized output, where it could execute when the content was loaded back into a page or editor.

### Proof of concept

```html
<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 124 124">
  <rect width="124" height="124" rx="24" fill="#000000"></rect>
  <script type="text/javascript">alert(document.domain);</script>
</svg>
```

Load the payload into the editor (e.g. via source mode) and the `<script>` is preserved in `editor.value` and executes.

### Impact

Stored / DOM cross-site scripting. An application that persists editor output and later renders or re-opens it in Jodit can have attacker-supplied script run in a victim's (e.g. an administrator's) authenticated browser context.

### Patch

Fixed in **4.13.6**: the deny/allow lookup now normalises the tag name to upper case before matching, so a foreign namespace can no longer bypass the filter, while `allowTags` is still honoured.

### Workaround

Upgrade to 4.13.6 or later. Server-side sanitization of stored HTML mitigates in the interim.

### Credit

Reported by Roman Kis (@CrownKingClown).

## References
- https://github.com/xdan/jodit/security/advisories/GHSA-45qg-252v-3f7p
- https://github.com/xdan/jodit/commit/49a31f451f6b686f5610022a1d4406ee85138dc5
- https://github.com/xdan/jodit
- https://github.com/xdan/jodit/releases/tag/4.13.6
