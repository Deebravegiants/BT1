# [H] Injection and Command Injection in devcert

## Summary
Severity: High
Advisory: GHSA-4228-7qvx-f4rq
CVE: CVE-2020-8186
CWE: CWE-74, CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-4228-7qvx-f4rq
Type: github-advisory

## Affected
- npm: `devcert` — affected >=0 <1.1.2

## Details
A command injection vulnerability in the `devcert` module may lead to remote code execution when users of the module pass untrusted input to the `certificateFor` function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8186
- https://hackerone.com/reports/863544
