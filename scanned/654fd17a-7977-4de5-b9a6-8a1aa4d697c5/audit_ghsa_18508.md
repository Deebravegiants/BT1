# [M] tarteaucitron.js vulnerable to DOM Clobbering via document.currentScript

## Summary
Severity: Medium
Advisory: GHSA-q43x-79jr-cq98
CVE: CVE-2025-48939
CWE: CWE-138
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2025-07-03
Source: https://github.com/advisories/GHSA-q43x-79jr-cq98
Type: github-advisory

## Affected
- npm: `tarteaucitronjs` — affected >=0 <1.22.0

## Details
A vulnerability was identified in tarteaucitron.js where document.currentScript was accessed without verifying that it referenced an actual `<script>` element. If an attacker injected an HTML element such as:

```
<img name="currentScript" src="https://malicious.example.com">
```

it could clobber the document.currentScript property. This causes the script to resolve incorrectly to an <img> element instead of the <script> tag, leading to unexpected behavior or failure to load the script path correctly.

This issue arises because in some browser environments, named DOM elements (e.g., name="currentScript") become properties on the global document object.

## Impact
An attacker with control over the HTML could exploit this to change the CDN domain of tarteaucitron.

## Fix https://github.com/AmauriC/tarteaucitron.js/commit/230a3b69d363837acfa895823d841e0608826ba3
The issue was resolved by verifying that document.currentScript is an instance of HTMLScriptElement. If not, the script now falls back safely to the last <script> tag on the page.

## References
- https://github.com/AmauriC/tarteaucitron.js/security/advisories/GHSA-q43x-79jr-cq98
- https://nvd.nist.gov/vuln/detail/CVE-2025-48939
- https://github.com/AmauriC/tarteaucitron.js/commit/230a3b69d363837acfa895823d841e0608826ba3
- https://github.com/AmauriC/tarteaucitron.js
