# [M] jsPDF Vulnerable to Stored XMP Metadata Injection (Spoofing & Integrity Violation)

## Summary
Severity: Medium
Advisory: GHSA-vm32-vv63-w422
CVE: CVE-2026-24043
CWE: CWE-20, CWE-74
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-vm32-vv63-w422
Type: github-advisory

## Affected
- npm: `jspdf` — affected >=0 <4.1.0

## Details
### Impact

User control of the first argument of the `addMetadata` function allows users to inject arbitrary XML.

If given the possibility to pass unsanitized input to the `addMetadata` method, a user can inject arbitrary XMP metadata into the generated PDF. If the generated PDF is signed, stored or otherwise processed after, the integrity of the PDF can no longer be guaranteed.

Example attack vector:

```js
import { jsPDF } from "jspdf"

const doc = new jsPDF()

// Input a string that closes the current XML tag and opens a new one.
// We are injecting a fake "dc:creator" (Author) to spoof the document source.
const maliciousInput = '</jspdf:metadata></rdf:Description>' +
    '<rdf:Description xmlns:dc="http://purl.org/dc/elements/1.1/">' +
    '<dc:creator>TRUSTED_ADMINISTRATOR</dc:creator>' + // <--- Spoofed Identity
    '</rdf:Description>' +
    '<rdf:Description><jspdf:metadata>'

// The application innocently adds the user's input to the metadata
doc.addMetadata(maliciousInput, "http://valid.namespace")

doc.save("test.pdf")
```

### Patches

The vulnerability has been fixed in jsPDF@4.1.0

### Workarounds

Sanitize user input before passing it to the `addMetadata` method: escape XML entities. For example:

```js
let input = "..."

input = input
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;")

doc.addMetadata(input)
```

## References
- https://github.com/parallax/jsPDF/security/advisories/GHSA-vm32-vv63-w422
- https://nvd.nist.gov/vuln/detail/CVE-2026-24043
- https://github.com/parallax/jsPDF/commit/efe54bf50f3f5e5416b2495e3c24624fc80b6cff
- https://github.com/parallax/jsPDF
- https://github.com/parallax/jsPDF/releases/tag/v4.1.0
