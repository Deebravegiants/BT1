# [H] Badaso CMS file upload vulnerability

## Summary
Severity: High
Advisory: GHSA-gqp9-jh35-439m
CVE: CVE-2025-52353
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-08-26
Source: https://github.com/advisories/GHSA-gqp9-jh35-439m
Type: github-advisory

## Affected
- Packagist: `badaso/core` — affected >=0

## Details
An arbitrary code execution vulnerability in Badaso CMS 2.9.11. The Media Manager allows authenticated users to upload files containing embedded PHP code via the file-upload endpoint, bypassing content-type validation. When such a file is accessed via its URL, the server executes the PHP payload, enabling an attacker to run arbitrary system commands and achieve full compromise of the underlying host. This has been demonstrated by embedding a backdoor within a PDF and renaming it with a .php extension.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-52353
- https://github.com/uasoft-indonesia/badaso
- https://medium.com/@pat.sanitjairak/remote-code-execution-in-a-plain-view-0f86f183543d
