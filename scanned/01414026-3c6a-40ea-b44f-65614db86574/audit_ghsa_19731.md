# [H] FastChat Server-Side Request Forgery vulnerability

## Summary
Severity: High
Advisory: GHSA-h254-g997-685c
CVE: CVE-2024-11603
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-h254-g997-685c
Type: github-advisory

## Affected
- PyPI: `fschat` — affected >=0

## Details
A Server-Side Request Forgery (SSRF) vulnerability exists in lm-sys/fastchat version 0.2.36. The vulnerability is present in the `/queue/join?` endpoint, where insufficient validation of the path parameter allows an attacker to send crafted requests. This can lead to unauthorized access to internal networks or the AWS metadata endpoint, potentially exposing sensitive data and compromising internal servers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-11603
- https://github.com/lm-sys/FastChat
- https://huntr.com/bounties/89f1158d-4a75-4000-a1bd-f82dd1a62bff
