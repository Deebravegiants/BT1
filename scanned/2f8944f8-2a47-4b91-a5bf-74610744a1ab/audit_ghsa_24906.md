# [M] Shiba vulnerable to XSS leading to code execution

## Summary
Severity: Medium
Advisory: GHSA-jr64-pggr-j8xj
CVE: CVE-2017-1000491
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-jr64-pggr-j8xj
Type: github-advisory

## Affected
- npm: `shiba` — affected >=0 <1.1.1

## Details
Shiba markdown live preview app version 1.1.0 is vulnerable to XSS which leads to code execution due to enabled node integration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000491
- https://github.com/rhysd/Shiba/issues/42
- https://github.com/rhysd/Shiba/commit/e8a65b0f81eb04903eedd29500d7e1bedf249eab
