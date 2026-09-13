# [C] jsPDF has Local File Inclusion/Path Traversal vulnerability

## Summary
Severity: Critical
Advisory: GHSA-f8cm-6447-x5h2
CVE: CVE-2025-68428
CWE: CWE-22, CWE-35, CWE-73
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-f8cm-6447-x5h2
Type: github-advisory

## Affected
- npm: `jspdf` — affected >=0 <4.0.0

## Details
### Impact
User control of the first argument of the loadFile method in the node.js build allows local file inclusion/path traversal.

If given the possibility to pass unsanitized paths to the loadFile method, a user can retrieve file contents of arbitrary files in the local file system the node process is running in. The file contents are included verbatim in the generated PDFs.

Other affected methods are: `addImage`, `html`, `addFont`.

Only the node.js builds of the library are affected, namely the `dist/jspdf.node.js` and `dist/jspdf.node.min.js` files.

Example attack vector:

```js
import { jsPDF } from "./dist/jspdf.node.js";

const doc = new jsPDF();

doc.addImage("./secret.txt", "JPEG", 0, 0, 10, 10);
doc.save("test.pdf"); // the generated PDF will contain the "secret.txt" file
```

### Patches
The vulnerability has been fixed in jsPDF@4.0.0. This version restricts file system access per default. This semver-major update does not introduce other breaking changes.

### Workarounds
With recent node versions, jsPDF recommends using the `--permission` flag in production. The feature was introduced experimentally in v20.0.0 and is stable since v22.13.0/v23.5.0/v24.0.0. See the [node documentation](https://nodejs.org/api/permissions.html) for details.

For older node versions, sanitize user-provided paths before passing them to jsPDF.

### Credits
Researcher: kilkat (Kwangwoon Kim)

## References
- https://github.com/parallax/jsPDF/security/advisories/GHSA-f8cm-6447-x5h2
- https://nvd.nist.gov/vuln/detail/CVE-2025-68428
- https://github.com/parallax/jsPDF/commit/a688c8f479929b24a6543b1fa2d6364abb03066d
- https://github.com/parallax/jsPDF
- https://github.com/parallax/jsPDF/releases/tag/v4.0.0
