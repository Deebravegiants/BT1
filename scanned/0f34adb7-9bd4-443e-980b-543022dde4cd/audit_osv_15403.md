# [H] CVE-2019-15892

## Summary
Severity: High
Advisory: CVE-2019-15892
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-03
Source: https://osv.dev/vulnerability/CVE-2019-15892
Type: osv

## Details
An issue was discovered in Varnish Cache before 6.0.4 LTS, and 6.1.x and 6.2.x before 6.2.1. An HTTP/1 parsing failure allows a remote attacker to trigger an assert by sending crafted HTTP/1 requests. The assert will cause an automatic restart with a clean cache, which makes it a Denial of Service attack.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00069.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00089.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3OEOCYRU43TWEU2C65F3D6GK64MSWNNK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DBAQF6UDRSTURGINIMSMLJR4PTDYWA7C/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KLSF54TDJWJLINIFEW5V5BKDNY5EQRR3/
- https://seclists.org/bugtraq/2019/Sep/5
- https://varnish-cache.org/security/VSV00003.html
- https://www.debian.org/security/2019/dsa-4514
