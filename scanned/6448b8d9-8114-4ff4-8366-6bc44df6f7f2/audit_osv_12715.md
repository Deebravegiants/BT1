# [H] CVE-2018-14463

## Summary
Severity: High
Advisory: CVE-2018-14463
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-03
Source: https://osv.dev/vulnerability/CVE-2018-14463
Type: osv

## Details
The VRRP parser in tcpdump before 4.9.3 has a buffer over-read in print-vrrp.c:vrrp_print() for VRRP version 2, a different vulnerability than CVE-2019-15167.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/62XY42U6HY3H2APR5EHNWCZ7SAQNMMJN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FNYXF3IY2X65IOD422SA6EQUULSGW7FN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/R2UDPOSGVJQIYC33SQBXMDXHH4QDSDMU/
- https://usn.ubuntu.com/4252-1/
- https://usn.ubuntu.com/4252-2/
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00050.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00053.html
- http://seclists.org/fulldisclosure/2019/Dec/26
- https://github.com/the-tcpdump-group/tcpdump/blob/tcpdump-4.9/CHANGES
- https://lists.debian.org/debian-lts-announce/2019/10/msg00015.html
- https://seclists.org/bugtraq/2019/Dec/23
- https://seclists.org/bugtraq/2019/Oct/28
- https://security.netapp.com/advisory/ntap-20200120-0001/
- https://support.apple.com/kb/HT210788
- https://www.debian.org/security/2019/dsa-4547
- https://github.com/the-tcpdump-group/tcpdump/commit/3de07c772166b7e8e8bb4b9d1d078f1d901b570b
