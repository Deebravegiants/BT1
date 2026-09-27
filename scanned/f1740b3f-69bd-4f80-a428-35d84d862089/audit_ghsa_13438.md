# [H] Heap buffer overflow in PaddlePaddle

## Summary
Severity: High
Advisory: GHSA-hh7p-hvm3-rg88
CVE: CVE-2023-38671
CWE: CWE-120, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-26
Source: https://github.com/advisories/GHSA-hh7p-hvm3-rg88
Type: github-advisory

## Affected
- PyPI: `paddlepaddle` — affected >=0 <2.5.0

## Details
Heap buffer overflow in paddle.trace in PaddlePaddle before 2.5.0. This flaw can lead to a denial of service, information disclosure, or more damage is possible.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38671
- https://github.com/PaddlePaddle/Paddle/commit/12549dfe3e87a4c30f852d2eca81d7f67c8daa87
- https://github.com/PaddlePaddle/Paddle
- https://github.com/PaddlePaddle/Paddle/blob/develop/security/advisory/pdsa-2023-003.md
- https://github.com/pypa/advisory-database/tree/main/vulns/paddlepaddle/PYSEC-2023-124.yaml
