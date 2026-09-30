# [H] Out-of-bounds read in admesh

## Summary
Severity: High
Advisory: GHSA-5jrq-582v-9767
CVE: CVE-2018-25033
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-05-09
Source: https://github.com/advisories/GHSA-5jrq-582v-9767
Type: github-advisory

## Affected
- PyPI: `admesh` — affected >=0 <0.98.5

## Details
ADMesh through 0.98.4 has a heap-based buffer over-read in stl_update_connects_remove_1 (called from stl_remove_degenerate) in connect.c in libadmesh.a.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25033
- https://github.com/admesh/admesh/issues/28
- https://github.com/admesh/admesh
- https://github.com/advisories/GHSA-5jrq-582v-9767
- https://github.com/pypa/advisory-database/tree/main/vulns/admesh/PYSEC-2022-182.yaml
- https://lists.debian.org/debian-lts-announce/2022/05/msg00029.html
