# [H] CVE-2021-3742

## Summary
Severity: High
Advisory: CVE-2021-3742
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-11-15
Source: https://osv.dev/vulnerability/CVE-2021-3742
Type: osv

## Details
A Server-Side Request Forgery (SSRF) vulnerability was discovered in chatwoot/chatwoot, affecting all versions prior to 2.5.0. The vulnerability allows an attacker to upload an SVG file containing a malicious SSRF payload. When the SVG file is used as an avatar and opened in a new tab, it can trigger the SSRF, potentially leading to host redirection.

## References
- https://huntr.com/bounties/1625472546121-chatwoot/chatwoot
- https://github.com/chatwoot/chatwoot/commit/6fdd4a29969be8423f31890b807d27d13627c50c
