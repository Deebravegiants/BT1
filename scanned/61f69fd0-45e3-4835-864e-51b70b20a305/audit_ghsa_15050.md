# [H] PaddlePaddle stack overflow in paddle.linalg.lu_unpack

## Summary
Severity: High
Advisory: GHSA-g57v-2687-jx33
CVE: CVE-2023-52307
CWE: CWE-120, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:L (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-g57v-2687-jx33
Type: github-advisory

## Affected
- PyPI: `PaddlePaddle` — affected >=0 <2.6.0

## Details
Stack overflow in paddle.linalg.lu_unpack in PaddlePaddle before 2.6.0. This flaw can lead to a denial of service, or even more damage.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-52307
- https://github.com/PaddlePaddle/Paddle/commit/6fdb316c8b0eb747e5324907e352824c9dba8215
- https://github.com/PaddlePaddle/Paddle
- https://github.com/PaddlePaddle/Paddle/blob/develop/security/advisory/pdsa-2023-016.md
- https://github.com/pypa/advisory-database/tree/main/vulns/paddlepaddle/PYSEC-2024-139.yaml
