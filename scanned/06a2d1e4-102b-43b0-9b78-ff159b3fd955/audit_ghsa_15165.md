# [C] Code Injection in paddlepaddle

## Summary
Severity: Critical
Advisory: GHSA-chj7-w3f6-cvfj
CVE: CVE-2024-0521
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-20
Source: https://github.com/advisories/GHSA-chj7-w3f6-cvfj
Type: github-advisory

## Affected
- PyPI: `paddlepaddle` — affected >=0 <2.6.0

## Details
The vulnerability arises from the way the url parameter is incorporated into the command string without proper validation or sanitization. If the url is constructed from untrusted sources, an attacker could potentially inject malicious commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-0521
- https://github.com/PaddlePaddle/Paddle
- https://huntr.com/bounties/a569c64b-1e2b-4bed-a19f-47fd5a3da453
