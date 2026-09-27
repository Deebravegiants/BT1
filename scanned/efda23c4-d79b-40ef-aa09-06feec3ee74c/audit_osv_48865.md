# [M] CVE-2018-16587

## Summary
Severity: Medium
Advisory: CVE-2018-16587
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2018-09-28
Source: https://osv.dev/vulnerability/CVE-2018-16587
Type: osv

## Details
In Open Ticket Request System (OTRS) 4.0.x before 4.0.32, 5.0.x before 5.0.30, and 6.0.x before 6.0.11, an attacker could send a malicious email to an OTRS system. If a user with admin permissions opens it, it causes deletions of arbitrary files that the OTRS web server user has write access to.

## References
- https://lists.debian.org/debian-lts-announce/2018/09/msg00033.html
- https://www.debian.org/security/2018/dsa-4317
- https://github.com/OTRS/otrs/commit/d9db0c6a15caafda7689320ecf61777993c33711
- https://community.otrs.com/security-advisory-2018-04-security-update-for-otrs-framework/
- https://github.com/OTRS/otrs/commit/a4a1a01f84fac7ab032570ee50b660e2ebb15c01
- https://github.com/OTRS/otrs/commit/d8cae00b0f78c2a07bb10cedb817304139395843
