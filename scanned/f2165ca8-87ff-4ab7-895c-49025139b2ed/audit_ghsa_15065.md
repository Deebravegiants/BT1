# [M] PaddlePaddle nullptr dereference in paddle.crop

## Summary
Severity: Medium
Advisory: GHSA-qppw-c37g-xwcc
CVE: CVE-2023-52312
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-qppw-c37g-xwcc
Type: github-advisory

## Affected
- PyPI: `PaddlePaddle` — affected >=0 <2.6.0

## Details
Nullptr dereference in paddle.crop in PaddlePaddle before 2.6.0. This flaw can cause a runtime crash and a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-52312
- https://github.com/PaddlePaddle/Paddle/commit/488a0ddc322b24659b6b0067fea3030d2f013cf4
- https://github.com/PaddlePaddle/Paddle
- https://github.com/PaddlePaddle/Paddle/blob/develop/security/advisory/pdsa-2023-021.md
- https://github.com/pypa/advisory-database/tree/main/vulns/paddlepaddle/PYSEC-2024-144.yaml
