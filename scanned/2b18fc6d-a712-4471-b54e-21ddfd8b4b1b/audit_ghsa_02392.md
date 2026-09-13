# [C] Code injection in topthink/think

## Summary
Severity: Critical
Advisory: GHSA-ch3r-vp46-8g22
CVE: CVE-2020-17952
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-09
Source: https://github.com/advisories/GHSA-ch3r-vp46-8g22
Type: github-advisory

## Affected
- Packagist: `topthink/think` — affected >=0

## Details
A remote code execution (RCE) vulnerability in /library/think/App.php of Twothink v2.0 allows attackers to execute arbitrary PHP code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-17952
- https://github.com/twothink/twothink/issues/1
- https://github.com/twothink/twothink
