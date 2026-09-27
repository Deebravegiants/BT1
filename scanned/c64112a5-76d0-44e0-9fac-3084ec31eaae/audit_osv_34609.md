# [H] Drawing-Captcha APP Host Header Injection in `/register` and `/confirm-email` Endpoints

## Summary
Severity: High
Advisory: CVE-2025-62428
Aliases: GHSA-5pj8-fc6g-vv7m
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-62428
Type: osv

## Details
Drawing-Captcha APP provides interactive, engaging verification for Web-Based Applications. The vulnerability is a Host Header Injection in the /register and /confirm-email endpoints. It allows an attacker to manipulate the Host header in HTTP requests to generate malicious email confirmation links. These links can redirect users to attacker-controlled domains. This vulnerability affects all users relying on email confirmation for account registration or verification. This vulnerability is fixed in 1.2.5-alpha-patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62428.json
- https://github.com/Drawing-Captcha/Drawing-Captcha-APP/security/advisories/GHSA-5pj8-fc6g-vv7m
- https://nvd.nist.gov/vuln/detail/CVE-2025-62428
- https://github.com/Drawing-Captcha/Drawing-Captcha-APP/issues/30
