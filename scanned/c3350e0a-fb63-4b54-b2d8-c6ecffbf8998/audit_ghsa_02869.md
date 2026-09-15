# [H] Policies not properly enforced in bluemonday

## Summary
Severity: High
Advisory: GHSA-x95h-979x-cf3j
CVE: CVE-2021-42576
CWE: CWE-20
Ecosystem: Go, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-19
Source: https://github.com/advisories/GHSA-x95h-979x-cf3j
Type: github-advisory

## Affected
- PyPI: `pybluemonday` — affected >=0 <0.0.8
- Go: `github.com/microcosm-cc/bluemonday` — affected >=0 <1.0.16

## Details
The bluemonday sanitizer before 1.0.16 for Go, and before 0.0.8 for Python (in pybluemonday), does not properly enforce policies associated with the SELECT, STYLE, and OPTION elements.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42576
- https://github.com/microcosm-cc/bluemonday/commit/c788a2a4d42e081ad54a31368478820bb4a42fb4
- https://docs.google.com/document/d/11SoX296sMS0XoQiQbpxc5pNxSdbJKDJkm5BDv0zrX50
- https://github.com/advisories/GHSA-x95h-979x-cf3j
- https://github.com/microcosm-cc/bluemonday
- https://github.com/pypa/advisory-database/tree/main/vulns/pybluemonday/PYSEC-2021-849.yaml
- https://pkg.go.dev/vuln/GO-2022-0588
- https://pypi.org/project/pybluemonday
