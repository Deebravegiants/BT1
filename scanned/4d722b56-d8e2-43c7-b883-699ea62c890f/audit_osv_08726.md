# [H] CVE-2016-5427

## Summary
Severity: High
Advisory: CVE-2016-5427
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/CVE-2016-5427
Type: osv

## Details
PowerDNS (aka pdns) Authoritative Server before 3.4.10 does not properly handle a . (dot) inside labels, which allows remote attackers to cause a denial of service (backend CPU consumption) via a crafted DNS query.

## References
- http://www.securityfocus.com/bid/92917
- http://www.securitytracker.com/id/1036761
- http://www.debian.org/security/2016/dsa-3664
- http://www.openwall.com/lists/oss-security/2016/09/09/3
- https://doc.powerdns.com/md/security/powerdns-advisory-2016-01/
- https://github.com/PowerDNS/pdns/commit/881b5b03a590198d03008e4200dd00cc537712f3
