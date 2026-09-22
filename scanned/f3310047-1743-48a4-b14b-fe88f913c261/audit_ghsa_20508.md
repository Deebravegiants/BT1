# [H] Incorrect Calculation in the MSR JavaScript Cryptography Library

## Summary
Severity: High
Advisory: GHSA-9x9j-836w-8f55
CVE: CVE-2020-1026
CWE: CWE-682
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-9x9j-836w-8f55
Type: github-advisory

## Affected
- npm: `msrcrypto` — affected >=0 <1.5.8

## Details
A Security Feature Bypass vulnerability exists in the MSR JavaScript Cryptography Library that is caused by multiple bugs in the library's Elliptic Curve Cryptography (ECC) implementation.An attacker could potentially abuse these bugs to learn information about a server's private ECC key (a key leakage attack) or craft an invalid ECDSA signature that nevertheless passes as valid.The security update addresses the vulnerability by fixing the bugs disclosed in the ECC implementation, aka `MSR JavaScript Cryptography Library Security Feature Bypass Vulnerability`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1026
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1026
