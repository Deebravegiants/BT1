# [M] Stored XSS in PySpector HTML Report Generation leads to Javascript Code Execution

## Summary
Severity: Medium
Advisory: GHSA-2gmv-2r3v-jxj2
CVE: CVE-2026-33140
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-2gmv-2r3v-jxj2
Type: github-advisory

## Affected
- PyPI: `pyspector` — affected >=0 <0.1.7

## Details
### Summary
PySpector versions `<= 0.1.6` are affected by a stored Cross-Site Scripting (XSS) vulnerability in the HTML report generator. When PySpector scans a Python file containing JavaScript payloads (i.e. inside a string passed to `eval()` ), the flagged code snippet is interpolated into the HTML report without sanitization. Opening the generated report in a browser causes the embedded JavaScript to execute in the browser's local file context.

### Impact
An attacker can craft a malicious Python file (for example, hosted in a public repository), designed to be scanned by PySpector. When a victim scans this file and opens the resulting HTML report, arbitrary JavaScript executes in their browser. While the `file://` context limits the attacker's ability to exfiltrate cookies or make credentialed requests, the following is still achievable:
- Arbitrary DOM manipulation
- Redirects to attacker-controlled pages
- Theft of locally accessible data via `fetch()` or `XMLHttpRequest` to `file://` paths (browser-dependent)

Any user of PySpector who scans untrusted code and generates HTML reports, is potentially affected.

### PoC

The following steps reproduce the vulnerability on PySpector `<= 0.1.6`:
1. Create a malicious Python file containing a JavaScript payload embedded in a string argument to `eval()`, and run PySpector against the file, generating an HTML report:
<img width="871" height="752" alt="image" src="https://github.com/user-attachments/assets/1b0a57f2-3632-4347-a9b7-6a94dc2e82b2" />
2. Open the generated HTML report in any browser:
<img width="1920" height="920" alt="image" src="https://github.com/user-attachments/assets/a4075c4a-6153-41b4-ad77-81d009d7a9f8" />

## References
- https://github.com/ParzivalHack/PySpector/security/advisories/GHSA-2gmv-2r3v-jxj2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33140
- https://github.com/ParzivalHack/PySpector
