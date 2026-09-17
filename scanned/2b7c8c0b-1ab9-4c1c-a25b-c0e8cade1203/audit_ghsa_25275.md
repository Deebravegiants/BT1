# [H] Boolector use after free

## Summary
Severity: High
Advisory: GHSA-g58x-799h-v9h6
CVE: CVE-2019-7560
CWE: CWE-416
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-g58x-799h-v9h6
Type: github-advisory

## Affected
- PyPI: `pyboolector` — affected >=0 <3.1.0

## Details
In parser/btorsmt2.c in Boolector 3.0.0, opening a specially crafted input file leads to a use after free in get_failed_assumptions or btor_delete.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7560
- https://github.com/Boolector/boolector/issues/28
- https://github.com/Boolector/boolector/issues/29
- https://github.com/boolector/boolector
- https://github.com/pypa/advisory-database/tree/main/vulns/pyboolector/PYSEC-2019-252.yaml
