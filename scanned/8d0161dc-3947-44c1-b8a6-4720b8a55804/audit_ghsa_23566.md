# [C] Maltego incorrectly shares a MISP connection across users in a remote-transform use case

## Summary
Severity: Critical
Advisory: GHSA-fj35-m94r-9h4c
CVE: CVE-2020-12889
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fj35-m94r-9h4c
Type: github-advisory

## Affected
- PyPI: `MISP-maltego` — affected >=0 <1.4.5

## Details
MISP MISP-maltego 1.4.4 incorrectly shares a MISP connection across users in a remote-transform use case. Version 1.4.5 contains a patch.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12889
- https://github.com/MISP/MISP-maltego/commit/3ccde66dab4096ab5663e69f352992cc73e1160b
- https://github.com/MISP/MISP-maltego
- https://github.com/advisories/GHSA-fj35-m94r-9h4c
- https://github.com/pypa/advisory-database/tree/main/vulns/misp-maltego/PYSEC-2020-66.yaml
