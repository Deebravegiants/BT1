# [C] CVE-2018-8828

## Summary
Severity: Critical
Advisory: CVE-2018-8828
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-20
Source: https://osv.dev/vulnerability/CVE-2018-8828
Type: osv

## Details
A Buffer Overflow issue was discovered in Kamailio before 4.4.7, 5.0.x before 5.0.6, and 5.1.x before 5.1.2. A specially crafted REGISTER message with a malformed branch or From tag triggers an off-by-one heap-based buffer overflow in the tmx_check_pretran function in modules/tmx/tmx_pretran.c.

## References
- https://usn.ubuntu.com/4240-1/
- https://github.com/EnableSecurity/advisories/tree/master/ES2018-05-kamailio-heap-overflow
- https://www.debian.org/security/2018/dsa-4148
- https://github.com/kamailio/kamailio/commit/e1d8008a09d9390ebaf698abe8909e10dfec4097
