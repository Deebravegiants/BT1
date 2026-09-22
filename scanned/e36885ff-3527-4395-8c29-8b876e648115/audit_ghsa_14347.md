# [C] froxlor/froxlor vulnerable to unrestricted upload of file with dangerous type

## Summary
Severity: Critical
Advisory: GHSA-qwvp-g9j7-28f6
CVE: CVE-2023-2034
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-14
Source: https://github.com/advisories/GHSA-qwvp-g9j7-28f6
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.0.14

## Details
Image files uploaded in froxlor/froxlor prior to 2.0.14 were not properly validated which could result in remote code execution via path manipulation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2034
- https://github.com/froxlor/froxlor/commit/f36bc61fc74c85a21c8d31448198b11f96eb3bc6
- https://github.com/Froxlor/Froxlor
- https://huntr.dev/bounties/aba6beaa-570e-4523-8128-da4d8e374ef6
