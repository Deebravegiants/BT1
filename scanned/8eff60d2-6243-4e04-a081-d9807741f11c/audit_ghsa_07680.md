# [M] jsPDF has Shared State Race Condition in addJS Plugin

## Summary
Severity: Medium
Advisory: GHSA-cjw8-79x6-5cj4
CVE: CVE-2026-24040
CWE: CWE-200, CWE-362
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-cjw8-79x6-5cj4
Type: github-advisory

## Affected
- npm: `jspdf` — affected >=0 <4.1.0

## Details
### Impact

The addJS method in the jspdf Node.js build utilizes a shared module-scoped variable (text) to store JavaScript content. When used in a concurrent environment (e.g., a Node.js web server), this variable is shared across all requests.

If multiple requests generate PDFs simultaneously, the JavaScript content intended for one user may be overwritten by a subsequent request before the document is generated. This results in Cross-User Data Leakage, where the PDF generated for User A contains the JavaScript payload (and any embedded sensitive data) intended for User B.

Typically, this only affects server-side environments, although the same race conditions might occur if jsPDF runs client-side.

```js
import { jsPDF } from "jspdf";

const docA = new jsPDF();
const docB = new jsPDF();

// 1. User A sets their script (stored in shared 'text' variable)
docA.addJS('console.log("Secret A");');

// 2. User B sets their script (overwrites shared 'text' variable)
docB.addJS('console.log("Secret B");');

// 3. User A saves their PDF (reads current 'text' variable)
docA.save("userA.pdf");

// Result: userA.pdf contains "Secret B" instead of "Secret A"
```

### Patches
The vulnerability has been fixed in jspdf@4.0.1. The fix moves the shared variable into the function scope, ensuring isolation between instances.

### Workarounds
Avoid using the addJS method in concurrent server-side environments. If usage is required, ensure requests are processed sequentially (e.g., using a queue) rather than in parallel.

## References
- https://github.com/parallax/jsPDF/security/advisories/GHSA-cjw8-79x6-5cj4
- https://nvd.nist.gov/vuln/detail/CVE-2026-24040
- https://github.com/parallax/jsPDF/commit/2863e5c26afef211a545e8c174ab4d5fce3b8c0e
- https://github.com/parallax/jsPDF
- https://github.com/parallax/jsPDF/releases/tag/v4.1.0
