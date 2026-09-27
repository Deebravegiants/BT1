# [H] Prefect CORS (Cross-Origin Resource Sharing) misconfiguration

## Summary
Severity: High
Advisory: GHSA-4v9f-r55g-g6hc
CVE: CVE-2024-8183
CWE: CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-4v9f-r55g-g6hc
Type: github-advisory

## Affected
- PyPI: `prefect` — affected >=3.0.0rc1 <3.0.3
- PyPI: `prefect` — affected >=0 <2.20.17

## Details
A CORS (Cross-Origin Resource Sharing) misconfiguration in prefecthq/prefect prior to version 3.0.3 allows unauthorized domains to access sensitive data. This vulnerability can lead to unauthorized access to the database, resulting in potential data leaks, loss of confidentiality, service disruption, and data integrity risks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8183
- https://github.com/PrefectHQ/prefect/issues/15074
- https://github.com/PrefectHQ/prefect/commit/8f159b404126d93964a4daace7619bc553fa318c
- https://github.com/prefecthq/prefect/commit/a69266e077169b8a32ad76b1dd3ea63b96d011c2
- https://github.com/PrefectHQ/prefect
- https://github.com/PrefectHQ/prefect/releases/tag/2.20.17
- https://huntr.com/bounties/b801de43-ff9f-4db9-b583-4797d4f7d3d2
