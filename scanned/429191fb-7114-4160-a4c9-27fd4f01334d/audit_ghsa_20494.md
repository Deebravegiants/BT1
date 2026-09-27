# [H] An authenticated user can execute arbitrary command in Gerapy

## Summary
Severity: High
Advisory: GHSA-756h-r2c9-qp5j
CVE: CVE-2021-32849
CWE: CWE-77, CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-756h-r2c9-qp5j
Type: github-advisory

## Affected
- PyPI: `gerapy` — affected >=0 <0.9.9

## Details
### Impact

An authenticated user can execute arbitrary command, see more in https://github.com/Gerapy/Gerapy/issues/211.

### Patches

Fixed in 0.9.9

## References
- https://github.com/Gerapy/Gerapy/security/advisories/GHSA-756h-r2c9-qp5j
- https://nvd.nist.gov/vuln/detail/CVE-2021-32849
- https://github.com/Gerapy/Gerapy/issues/197
- https://github.com/Gerapy/Gerapy/issues/217
- https://github.com/Gerapy/Gerapy
- https://github.com/pypa/advisory-database/tree/main/vulns/gerapy/PYSEC-2022-17.yaml
- https://lgtm.com/projects/g/Gerapy/Gerapy?mode=tree&ruleFocus=1505994646253
- https://securitylab.github.com/advisories/GHSL-2021-076-gerapy
