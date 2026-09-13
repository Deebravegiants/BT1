# [H] HyperLPR Denial of Service vulnerability

## Summary
Severity: High
Advisory: GHSA-cg4p-5qfm-pjjj
CVE: CVE-2024-10713
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-cg4p-5qfm-pjjj
Type: github-advisory

## Affected
- PyPI: `hyperlpr3` — affected >=0

## Details
A vulnerability in szad670401/hyperlpr v3.0 allows for a Denial of Service (DoS) attack. The server fails to handle excessive characters appended to the end of multipart boundaries, regardless of the character used. This flaw can be exploited by sending malformed multipart requests with arbitrary characters at the end of the boundary, leading to excessive resource consumption and a complete denial of service for all users. The vulnerability is unauthenticated, meaning no user login or interaction is required for an attacker to exploit this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10713
- https://github.com/szad670401/HyperLPR/blob/9307450f7b7915be18f23a539ec05b41fe6629f4/Prj-Python/hyperlpr3/command/serve.py#L95
- https://github.com/szad670401/hyperlpr
- https://huntr.com/bounties/d5404069-95b3-40e0-a7a4-c3a183d861b0
