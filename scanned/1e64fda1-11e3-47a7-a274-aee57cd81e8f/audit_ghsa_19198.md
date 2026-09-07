# [C] DocsGPT Allows Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-9gff-5v8w-x922
CVE: CVE-2025-0868
CWE: CWE-77, CWE-95
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-20
Source: https://github.com/advisories/GHSA-9gff-5v8w-x922
Type: github-advisory

## Affected
- npm: `docsgpt` — affected >=0.8.1

## Details
A vulnerability, that could result in Remote Code Execution (RCE), has been found in DocsGPT. Due to improper parsing of JSON data using eval() an unauthorized attacker could send arbitrary Python code to be executed via /api/remote endpoint.

This issue affects DocsGPT: from 0.8.1 through 0.12.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-0868
- https://cert.pl/en/posts/2025/02/CVE-2025-0868
- https://cert.pl/posts/2025/02/CVE-2025-0868
- https://github.com/arc53/DocsGPT
- https://github.com/arc53/docsgpt
