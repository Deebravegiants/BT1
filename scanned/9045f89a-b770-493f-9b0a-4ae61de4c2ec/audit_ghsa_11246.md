# [H] jsPDF has a PDF Object Injection via FreeText color

## Summary
Severity: High
Advisory: GHSA-7x6v-j9x4-qf24
CVE: CVE-2026-31898
CWE: CWE-116
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-7x6v-j9x4-qf24
Type: github-advisory

## Affected
- npm: `jspdf` — affected >=0 <4.2.1

## Details
### Impact

User control of arguments of the `createAnnotation` method allows users to inject arbitrary PDF objects, such as JavaScript actions.

If given the possibility to pass unsanitized input to the following method, a user can inject arbitrary PDF objects, such as JavaScript actions, which might trigger when the PDF is opened or interacted with..

* `createAnnotation`: `color` parameter

Example attack vector:

```js
import { jsPDF } from 'jspdf'

const doc = new jsPDF();

const payload = '000000) /AA <</E <</S /Launch /F (calc.exe)>>>> (';

doc.createAnnotation({
  type: 'freetext',
  bounds: { x: 10, y: 10, w: 120, h: 20 },
  contents: 'hello',
  color: payload
});

doc.save('test.pdf');
```

### Patches

The vulnerability has been fixed in jsPDF@4.2.1.

### Workarounds
Sanitize user input before passing it to the vulnerable API members.

## References
- https://github.com/parallax/jsPDF/security/advisories/GHSA-7x6v-j9x4-qf24
- https://nvd.nist.gov/vuln/detail/CVE-2026-31898
- https://github.com/parallax/jsPDF/commit/4155c4819d5eca284168e51e0e1e81126b4f14b8
- https://github.com/parallax/jsPDF
- https://github.com/parallax/jsPDF/blob/b1607a9391d4cd65ea7ade25998aea8345ae1be3/src/modules/annotations.js#L193-L208
- https://github.com/parallax/jsPDF/releases/tag/v4.2.1
