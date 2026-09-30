# [H] Trestle has Server-Side Template Injection (SSTI) via Recursive Template Re-evaluation of Untrusted Data

## Summary
Severity: High
Advisory: CVE-2026-54757
Aliases: GHSA-jw39-3688-r4rx, PYSEC-2026-3817
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-54757
Type: osv

## Details
Compliance-trestle (Trestle) is a Python SDK and command-line tool for managing OSCAL compliance documents. In versions before 3.12.4 and versions 4.0.0 through 4.0.3, Trestle is vulnerable to server-side template injection that can lead to remote code execution. This occurs because the MDCleanInclude and MDSectionInclude Jinja2 tags re-parse untrusted Markdown content as template source code using a non-sandboxed jinja2.Environment. An attacker who controls content that Trestle renders, such as a crafted workspace Markdown file, a third-party SSP document, or a YAML lookup-table value, can inject a Jinja2 expression that traverses Python object internals to execute arbitrary operating system commands in the context of the Trestle process. This issue is fixed in versions 3.12.4 and 4.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54757.json
- https://github.com/oscal-compass/compliance-trestle/security/advisories/GHSA-jw39-3688-r4rx
- https://nvd.nist.gov/vuln/detail/CVE-2026-54757
- https://github.com/oscal-compass/compliance-trestle/commit/0f82d19bd42f9cc0f1b3acd7fc3f6dafe3b6ae10
- https://github.com/oscal-compass/compliance-trestle/commit/5335ff873a2a68eb7de43df029bea09cadff22fd
