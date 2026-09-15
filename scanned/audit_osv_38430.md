# [H] TypeBot: Stored Cross-Site Scripting (XSS) via SVG File Upload On Profile Picture Form

## Summary
Severity: High
Advisory: CVE-2026-39970
Aliases: GHSA-jj87-c343-26vp
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-22
Source: https://osv.dev/vulnerability/CVE-2026-39970
Type: osv

## Details
TypeBot is a chatbot builder tool. Versions 3.15.2 and prior contain a critical stored XSS vulnerability in the app.typebot.io profile picture upload form. The application fails to sanitize or restrict SVG/XML-based uploads and directly renders them when accessed through the domain. By uploading a crafted malicious SVG file containing embedded JavaScript, an attacker will execute arbitrary JavaScript code. This vulnerability directly enables stored XSS exploitation because the payload is persistently stored on your infrastructure (app.typebot.io) and accessible from a public-facing, permanent link. Stored XSS via malicious SVG uploads to app.typebot.io allows attackers to execute arbitrary JavaScript in victims' browsers, enabling session/token theft, account takeover, and exfiltration of sensitive user data. This issue has been fixed in version 3.16.0.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.16.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39970.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-jj87-c343-26vp
- https://nvd.nist.gov/vuln/detail/CVE-2026-39970
