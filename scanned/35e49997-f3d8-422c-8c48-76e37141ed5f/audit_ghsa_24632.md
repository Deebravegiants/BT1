# [C] AdaptiveScale LXDUI Hardcoded JWT Secret Key

## Summary
Severity: Critical
Advisory: GHSA-p4xh-4869-8vrg
CVE: CVE-2021-40494
CWE: CWE-798
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p4xh-4869-8vrg
Type: github-advisory

## Affected
- PyPI: `lxdui` — affected >=0

## Details
A Hardcoded JWT Secret Key in `__metadata__.py` metadata.py in AdaptiveScale LXDUI through 2.1.3 allows attackers to gain admin access to the host system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40494
- https://github.com/AdaptiveScale/lxdui/pull/353
- https://github.com/AdaptiveScale/lxdui/commit/e4bffeb9d69a5700a642cb6424453d1894e50d84
- https://github.com/AdaptiveScale/lxdui
- https://github.com/pypa/advisory-database/tree/main/vulns/lxdui/PYSEC-2021-342.yaml
