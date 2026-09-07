# [M] Layui has DOM Clobbering gadgets that leads to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-j827-6rgf-9629
CVE: CVE-2024-47075
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2024-09-26
Source: https://github.com/advisories/GHSA-j827-6rgf-9629
Type: github-advisory

## Affected
- npm: `layui` — affected >=0 <2.9.17

## Details
### Summary
A DOM Clobbering vulnerability has been discovered in `layui` that can lead to Cross-site Scripting (XSS) on web pages where attacker-controlled HTML elements (e.g., `img` tags with unsanitized `name` attributes) are present.

It's worth noting that we’ve identifed similar issues in other popular client-side libraries like Webpack ([CVE-2024-43788](https://github.com/webpack/webpack/security/advisories/GHSA-4vvj-4cpr-p986)) and Vite ([CVE-2024-45812](https://github.com/vitejs/vite/security/advisories/GHSA-64vr-g452-qvp3)), which might serve as valuable references.

###  Backgrounds

DOM Clobbering is a type of code-reuse attack where the attacker first embeds a piece of non-script, seemingly benign HTML markups in the webpage (e.g. through a post or comment) and leverages the gadgets (pieces of js code snippet) living in the existing libraries to transform it into executable code. 

### Impact

This vulnerability can lead to cross-site scripting (XSS) on websites that uses `layui` library and allow users to inject certain scriptless HTML tags with improperly sanitized `name` or `id` attributes.

### Patch

This problem has been patched in Layui 2.9.17. You can find the official fix announcement at: 
https://layui.dev/notes/share/security-currentscript.html

## References
- https://github.com/layui/layui/security/advisories/GHSA-j827-6rgf-9629
- https://nvd.nist.gov/vuln/detail/CVE-2024-47075
- https://github.com/layui/layui/commit/f756b41d63bf3d488a2cb042918638c9851bf2b0
- https://github.com/layui/layui
- https://layui.dev/notes/share/security-currentscript.html
