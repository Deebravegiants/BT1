# [M] CVE-2018-19519

## Summary
Severity: Medium
Advisory: CVE-2018-19519
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-11-25
Source: https://osv.dev/vulnerability/CVE-2018-19519
Type: osv

## Details
In tcpdump 4.9.2, a stack-based buffer over-read exists in the print_prefix function of print-hncp.c via crafted packet data because of missing initialization.

## References
- https://kb.pulsesecure.net/articles/Pulse_Security_Advisories/SA44516
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/62XY42U6HY3H2APR5EHNWCZ7SAQNMMJN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FNYXF3IY2X65IOD422SA6EQUULSGW7FN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/R2UDPOSGVJQIYC33SQBXMDXHH4QDSDMU/
- https://usn.ubuntu.com/4252-1/
- https://usn.ubuntu.com/4252-2/
- http://www.securityfocus.com/bid/106098
- https://access.redhat.com/errata/RHSA-2019:3976
- https://github.com/zyingp/temp/blob/master/tcpdump.md
