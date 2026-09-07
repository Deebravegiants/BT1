# [M] Tendenci CMS contains a stored Cross-site Scripting (XSS) vulnerability in the Forums module

## Summary
Severity: Medium
Advisory: GHSA-6fvp-wmh6-jg95
CVE: CVE-2025-70960
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-6fvp-wmh6-jg95
Type: github-advisory

## Affected
- PyPI: `tendenci` — affected >=0

## Details
A stored cross-site scripting (XSS) vulnerability in the Forums module of Tendenci CMS v15.3.7 allows attackers to execute arbitrary web scripts or HTML via injecting a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-70960
- https://github.com/emirhanyucelll/tendenci/blob/main/Readme.md
- https://github.com/tendenci/tendenci
