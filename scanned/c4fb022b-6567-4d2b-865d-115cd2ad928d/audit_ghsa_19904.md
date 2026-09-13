# [H] FastChat Uncontrolled Resource Consumption vulnerability

## Summary
Severity: High
Advisory: GHSA-qg86-f892-m4hj
CVE: CVE-2024-10907
CWE: CWE-400, CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-qg86-f892-m4hj
Type: github-advisory

## Affected
- PyPI: `fschat` — affected >=0

## Details
In lm-sys/fastchat Release v0.2.36, the server fails to handle excessive characters appended to the end of multipart boundaries. This flaw can be exploited by sending malformed multipart requests with arbitrary characters at the end of the boundary. Each extra character is processed in an infinite loop, leading to excessive resource consumption and a complete denial of service (DoS) for all users. The vulnerability is unauthenticated, meaning no user login or interaction is required for an attacker to exploit this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10907
- https://github.com/lm-sys/FastChat
- https://huntr.com/bounties/bf3ca81d-3508-4455-95d9-0b653e46d6e4
