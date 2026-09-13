# [H] CVE-2019-12175

## Summary
Severity: High
Advisory: CVE-2019-12175
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-07-17
Source: https://osv.dev/vulnerability/CVE-2019-12175
Type: osv

## Details
In Zeek Network Security Monitor (formerly known as Bro) before 2.6.2, a NULL pointer dereference in the Kerberos (aka KRB) protocol parser leads to DoS because a case-type index is mishandled.

## References
- https://github.com/zeek/zeek/releases/tag/v2.6.2
