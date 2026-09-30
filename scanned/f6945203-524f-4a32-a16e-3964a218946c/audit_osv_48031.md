# [H] CVE-2017-17476

## Summary
Severity: High
Advisory: CVE-2017-17476
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-20
Source: https://osv.dev/vulnerability/CVE-2017-17476
Type: osv

## Details
Open Ticket Request System (OTRS) 4.0.x before 4.0.28, 5.0.x before 5.0.26, and 6.0.x before 6.0.3, when cookie support is disabled, might allow remote attackers to hijack web sessions and consequently gain privileges via a crafted email.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00018.html
- https://www.debian.org/security/2017/dsa-4069
- https://www.otrs.com/security-advisory-2017-10-security-update-otrs-framework/
- https://github.com/OTRS/otrs/commit/26707eaaa791648e6c7ad6aeaa27efd70e7c66eb
- https://github.com/OTRS/otrs/commit/36e3be99cfe8a9e09afa1b75fdc39f3e28f561fc
- https://github.com/OTRS/otrs/commit/720c73fbf53e476ca7dfdf2ae1d4d3d2aad2b953
