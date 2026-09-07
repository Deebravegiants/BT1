# [H] mat2 before 0.13.0 allows directory traversal during the ZIP archive cleaning process.

## Summary
Severity: High
Advisory: GHSA-f33p-9287-h552
CVE: CVE-2022-35410
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-07-12
Source: https://github.com/advisories/GHSA-f33p-9287-h552
Type: github-advisory

## Affected
- PyPI: `mat2` — affected >=0 <0.13.0

## Details
mat2 (aka metadata anonymisation toolkit) before 0.13.0 allows `../` directory traversal during the ZIP archive cleaning process. This primarily affects mat2 web instances, in which clients could obtain sensitive information via a crafted archive.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35410
- https://0xacab.org/jvoisin/mat2
- https://0xacab.org/jvoisin/mat2/-/commit/beebca4bf1cd3b935824c966ce077e7bcf610385
- https://0xacab.org/jvoisin/mat2/-/issues/174
- https://dustri.org/b/mat2-0130.html
- https://github.com/advisories/GHSA-f33p-9287-h552
- https://github.com/pypa/advisory-database/tree/main/vulns/mat2/PYSEC-2022-223.yaml
- https://www.debian.org/security/2022/dsa-5185
