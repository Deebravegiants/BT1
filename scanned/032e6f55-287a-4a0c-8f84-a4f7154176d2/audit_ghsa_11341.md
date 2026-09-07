# [C] jsPDF has HTML Injection in New Window paths

## Summary
Severity: Critical
Advisory: GHSA-wfv2-pwc8-crg5
CVE: CVE-2026-31938
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-wfv2-pwc8-crg5
Type: github-advisory

## Affected
- npm: `jspdf` — affected >=0 <4.2.1

## Details
### Impact

User control of the `options` argument of the `output` function allows attackers to inject arbitrary HTML (such as scripts) into the browser context the created PDF is opened in. The affected overloads and options are:

* `"pdfobjectnewwindow"`: the `pdfObjectUrl` option and the entire options object, which is JSON-serialized and included verbatim in the generated HTML-string.
* `"pdfjsnewwindow"`: the `pdfJsUrl` and `filename` options
* `"dataurlnewwindow"`: the `filename` option

The vulnerability can be exploited in the following scenario: the attacker provides values for the output options, for example via a web interface. These values are then passed unsanitized (automatically or semi-automatically) to the attack victim. The victim creates and opens a PDF with the attack vector using one of the vulnerable method overloads inside their browser. The attacker can thus inject scripts that run in the victims browser context and can extract or modify secrets from this context.

Example attack vector:

```js
import { jsPDF } from 'jspdf';
const doc = new jsPDF();

const payload =  'x\"></iframe><script>window.__n=1</script><iframe src="';

doc.output('pdfjsnewwindow', {
  filename: payload,
  pdfJsUrl: 'viewer.html'
});
```

### Patches
The vulnerability has been fixed in jspdf@4.2.1.

### Workarounds
Sanitize user input before passing it to the output method.

## References
- https://github.com/parallax/jsPDF/security/advisories/GHSA-wfv2-pwc8-crg5
- https://nvd.nist.gov/vuln/detail/CVE-2026-31938
- https://github.com/parallax/jsPDF/commit/87a40bbd07e6b30575196370670b41f264aa78d7
- https://github.com/parallax/jsPDF
- https://github.com/parallax/jsPDF/releases/tag/v4.2.1
