# [M] CVE-2020-8619

## Summary
Severity: Medium
Advisory: CVE-2020-8619
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-17
Source: https://osv.dev/vulnerability/CVE-2020-8619
Type: osv

## Details
In ISC BIND9 versions BIND 9.11.14 -> 9.11.19, BIND 9.14.9 -> 9.14.12, BIND 9.16.0 -> 9.16.3, BIND Supported Preview Edition 9.11.14-S1 -> 9.11.19-S1: Unless a nameserver is providing authoritative service for one or more zones and at least one zone contains an empty non-terminal entry containing an asterisk ("*") character, this defect cannot be encountered. A would-be attacker who is allowed to change zone content could theoretically introduce such a record in order to exploit this condition to cause denial of service, though we consider the use of this vector unlikely because any such attack would require a significant privilege level and be easily traceable.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CNFTTYJ5JJJJ6QG3AHXJGDIIEYMDFWFW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EIOXMJX4N3LBKC65OXNBE52W4GAS7QEX/
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00041.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00044.html
- https://kb.isc.org/docs/cve-2020-8619
- https://security.netapp.com/advisory/ntap-20200625-0003/
- https://usn.ubuntu.com/4399-1/
- https://www.debian.org/security/2020/dsa-4752
