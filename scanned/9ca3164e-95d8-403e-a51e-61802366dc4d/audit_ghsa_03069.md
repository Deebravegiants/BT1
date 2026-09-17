# [H] Code injection in blamer

## Summary
Severity: High
Advisory: GHSA-7vm7-j8p7-h346
CVE: CVE-2020-8137
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-7vm7-j8p7-h346
Type: github-advisory

## Affected
- npm: `blamer` — affected >=0 <1.0.1

## Details
Code injection vulnerability in blamer 1.0.0 and earlier may result in remote code execution when the input can be controlled by an attacker.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8137
- https://hackerone.com/reports/772448
