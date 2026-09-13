# [M] CVE-2017-16808

## Summary
Severity: Medium
Advisory: CVE-2017-16808
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-11-13
Source: https://osv.dev/vulnerability/CVE-2017-16808
Type: osv

## Details
tcpdump before 4.9.3 has a heap-based buffer over-read related to aoe_print in print-aoe.c and lookup_emem in addrtoname.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00065.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00050.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00053.html
- http://packetstormsecurity.com/files/154710/Slackware-Security-Advisory-tcpdump-Updates.html
- http://seclists.org/fulldisclosure/2019/Dec/26
- https://github.com/the-tcpdump-group/tcpdump/blob/tcpdump-4.9/CHANGES
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/62XY42U6HY3H2APR5EHNWCZ7SAQNMMJN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FNYXF3IY2X65IOD422SA6EQUULSGW7FN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/R2UDPOSGVJQIYC33SQBXMDXHH4QDSDMU/
- https://seclists.org/bugtraq/2019/Dec/23
- https://seclists.org/bugtraq/2019/Oct/2
- https://support.apple.com/kb/HT210788
- https://usn.ubuntu.com/4252-1/
- https://usn.ubuntu.com/4252-2/
- http://www.securitytracker.com/id/1039773
- https://github.com/the-tcpdump-group/tcpdump/issues/645
