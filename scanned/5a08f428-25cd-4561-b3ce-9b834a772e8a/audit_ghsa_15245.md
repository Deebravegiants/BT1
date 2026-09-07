# [C] PaddlePaddle command injection in get_online_pass_interval

## Summary
Severity: Critical
Advisory: GHSA-j5h9-9r39-43q5
CVE: CVE-2023-52310
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-j5h9-9r39-43q5
Type: github-advisory

## Affected
- PyPI: `PaddlePaddle` — affected >=0 <2.6.0

## Details
PaddlePaddle before 2.6.0 has a command injection in get_online_pass_interval. This resulted in the ability to execute arbitrary commands on the operating system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-52310
- https://github.com/PaddlePaddle/Paddle/commit/49bec176053595975c1941cff9749c55f7203ea9
- https://github.com/PaddlePaddle/Paddle
- https://github.com/PaddlePaddle/Paddle/blob/develop/security/advisory/pdsa-2023-019.md
- https://github.com/pypa/advisory-database/tree/main/vulns/paddlepaddle/PYSEC-2024-142.yaml
