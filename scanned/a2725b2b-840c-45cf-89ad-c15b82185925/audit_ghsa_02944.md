# [M] Information disclosure vulnerability in OnionShare

## Summary
Severity: Medium
Advisory: GHSA-6rvj-pw9w-jcvc
CVE: CVE-2021-41867
CWE: CWE-200
Ecosystem: PyPI
Published: 2021-11-19
Source: https://github.com/advisories/GHSA-6rvj-pw9w-jcvc
Type: github-advisory

## Affected
- PyPI: `onionshare-cli` — affected >=2.3 <2.4

## Details
An information disclosure vulnerability in OnionShare 2.3 before 2.4 allows remote unauthenticated attackers to retrieve the full list of participants of a non-public OnionShare node via the --chat feature.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41867
- https://github.com/onionshare/onionshare
- https://github.com/onionshare/onionshare/compare/v2.3.3...v2.4
- https://www.ihteam.net/advisory/onionshare
