# [C] pipreqs vulnerable to Dependency Confusion

## Summary
Severity: Critical
Advisory: GHSA-v4f4-23wc-99mh
CVE: CVE-2023-31543
CWE: CWE-427
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-30
Source: https://github.com/advisories/GHSA-v4f4-23wc-99mh
Type: github-advisory

## Affected
- PyPI: `pipreqs` — affected >=0.3.0 <0.4.12

## Details
A dependency confusion in pipreqs v0.3.0 to v0.4.11 allows attackers to execute arbitrary code via uploading a crafted PyPI package to the chosen repository server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31543
- https://github.com/bndr/pipreqs/pull/364
- https://github.com/bndr/pipreqs/commit/3f5964fcb90ec6eb6df46d78e651a1b73538d0ba
- https://gist.github.com/adeadfed/ccc834440af354a5638f889bee34bafe
- https://github.com/bndr/pipreqs
- https://github.com/bndr/pipreqs/blob/master/pipreqs/pipreqs.py#L447-L449
- https://github.com/pypa/advisory-database/tree/main/vulns/pipreqs/PYSEC-2023-99.yaml
