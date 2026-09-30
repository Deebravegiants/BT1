# [H] CVE-2017-6384

## Summary
Severity: High
Advisory: CVE-2017-6384
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-02
Source: https://osv.dev/vulnerability/CVE-2017-6384
Type: osv

## Details
Memory leak in the login_user function in saslserv/main.c in saslserv/main.so in Atheme 7.2.7 allows a remote unauthenticated attacker to consume memory and cause a denial of service. This is fixed in 7.2.8.

## References
- http://www.securityfocus.com/bid/96552
- https://github.com/atheme/atheme/pull/539
- https://github.com/atheme/atheme/releases/tag/v7.2.8
