# [H] jsPDF Vulnerable to Denial of Service (DoS) via Unvalidated BMP Dimensions in BMPDecoder

## Summary
Severity: High
Advisory: GHSA-95fx-jjr5-f39c
CVE: CVE-2026-24133
CWE: CWE-20, CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-95fx-jjr5-f39c
Type: github-advisory

## Affected
- npm: `jspdf` — affected >=0 <4.1.0

## Details
### Impact

User control of the first argument of the `addImage` method results in Denial of Service.

If given the possibility to pass unsanitized image data or URLs to the `addImage` method, a user can provide a harmful BMP file that results in out of memory errors and denial of service. Harmful BMP files have large width and/or height entries in their headers, wich lead to excessive memory allocation.

Other affected methods are: `html`.

Example attack vector:

```js
import { jsPDF } from "jspdf" 

// malicious BMP image data with large width/height headers
const payload = ...

const doc = new jsPDF();

doc.addImage(payload, "BMP", 0, 0, 100, 100);
```

### Patches

The vulnerability has been fixed in jsPDF 4.1.0. Upgrade to jspdf@>=4.1.0.

### Workarounds

Sanitize image data or URLs before passing it to the addImage method or one of the other affected methods.

## References
- https://github.com/parallax/jsPDF/security/advisories/GHSA-95fx-jjr5-f39c
- https://nvd.nist.gov/vuln/detail/CVE-2026-24133
- https://github.com/parallax/jsPDF/commit/ae4b93f76d8fc1baa5614bd5fdb5d174c3b85f0d
- https://github.com/parallax/jsPDF
- https://github.com/parallax/jsPDF/releases/tag/v4.1.0
