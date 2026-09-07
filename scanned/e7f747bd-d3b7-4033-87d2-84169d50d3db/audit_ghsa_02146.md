# [M] Cross Site Scripting (XSS) in Quokka

## Summary
Severity: Medium
Advisory: GHSA-5m69-3chg-6f8m
CVE: CVE-2020-18702
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-5m69-3chg-6f8m
Type: github-advisory

## Affected
- PyPI: `quokka` — affected >=0

## Details
Cross Site Scripting (XSS) in Quokka v0.4.0 allows remote attackers to execute arbitrary code via the 'Username' parameter in the component 'quokka/admin/actions.py'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-18702
- https://github.com/rochacbruno/quokka/issues/675
- https://github.com/advisories/GHSA-5m69-3chg-6f8m
- https://github.com/pypa/advisory-database/tree/main/vulns/quokka/PYSEC-2021-143.yaml
- https://github.com/rochacbruno/quokka
