# [M] Firefly III vulnerable to reflected cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-mrc2-h7q2-pp97
CVE: CVE-2019-13646
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mrc2-h7q2-pp97
Type: github-advisory

## Affected
- Packagist: `grumpydictator/firefly-iii` — affected >=0 <4.7.17.3

## Details
Firefly III before 4.7.17.3 is vulnerable to reflected XSS due to lack of filtration of user-supplied data in a search query.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13646
- https://github.com/firefly-iii/firefly-iii/issues/2339
- https://github.com/firefly-iii/firefly-iii/commit/f795cb07e1bb9ad3bd0dceeafbb0ece4ebe518d7
- https://github.com/firefly-iii/firefly-iii
- https://github.com/firefly-iii/firefly-iii/compare/a70b7cc...7d482aa
