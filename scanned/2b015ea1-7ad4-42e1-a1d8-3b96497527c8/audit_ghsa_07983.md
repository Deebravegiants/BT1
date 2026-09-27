# [H] jsPDF Affected by Client-Side/Server-Side Denial of Service via Malicious GIF Dimensions

## Summary
Severity: High
Advisory: GHSA-67pg-wm7f-q7fj
CVE: CVE-2026-25535
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-67pg-wm7f-q7fj
Type: github-advisory

## Affected
- npm: `jspdf` — affected >=0 <4.2.0

## Details
### Impact

User control of the first argument of the `addImage` method results in denial of service.

If given the possibility to pass unsanitized image data or URLs to the `addImage` method, a user can provide a harmful GIF file that results in out of memory errors and denial of service. Harmful GIF files have large width and/or height entries in their headers, wich lead to excessive memory allocation.

Other affected methods are: `html`.

Example attack vector:

```js
import { jsPDF } from "jspdf" 

// malicious GIF image data with large width/height headers
const payload = ...

const doc = new jsPDF();

doc.addImage(payload, "GIF", 0, 0, 100, 100);
```

### Patches

The vulnerability has been fixed in jsPDF 4.1.1. Upgrade to jspdf@>=4.2.0.

### Workarounds

Sanitize image data or URLs before passing it to the addImage method or one of the other affected methods.
### References
https://github.com/ZeroXJacks/CVEs/blob/main/2026/CVE-2026-25535.md

## References
- https://github.com/parallax/jsPDF/security/advisories/GHSA-67pg-wm7f-q7fj
- https://nvd.nist.gov/vuln/detail/CVE-2026-25535
- https://github.com/parallax/jsPDF/commit/2e5e156e284d92c7d134bce97e6418756941d5e6
- https://github.com/ZeroXJacks/CVEs/blob/main/2026/CVE-2026-25535.md
- https://github.com/parallax/jsPDF
- https://github.com/parallax/jsPDF/releases/tag/v4.2.0
