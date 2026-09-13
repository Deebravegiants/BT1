# [H] Sanic arbitrary file read and directory traversal

## Summary
Severity: High
Advisory: GHSA-mpmf-hr8p-p49g
CVE: CVE-2017-16762
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-mpmf-hr8p-p49g
Type: github-advisory

## Affected
- PyPI: `sanic` — affected >=0 <0.5.1

## Details
Sanic before 0.5.1 allows reading arbitrary files with directory traversal, as demonstrated by the `/static/..%2f` substring.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16762
- https://github.com/channelcat/sanic/issues/633
- https://github.com/sanic-org/sanic/pull/635
- https://github.com/channelcat/sanic/releases/tag/0.5.1
- https://github.com/pypa/advisory-database/tree/main/vulns/sanic/PYSEC-2017-40.yaml
- https://github.com/sanic-org/sanic
