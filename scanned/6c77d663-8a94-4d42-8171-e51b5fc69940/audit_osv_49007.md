# [H] CVE-2018-20103

## Summary
Severity: High
Advisory: CVE-2018-20103
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-12
Source: https://osv.dev/vulnerability/CVE-2018-20103
Type: osv

## Details
An issue was discovered in dns.c in HAProxy through 1.8.14. In the case of a compressed pointer, a crafted packet can trigger infinite recursion by making the pointer point to itself, or create a long chain of valid pointers resulting in stack exhaustion.

## References
- http://git.haproxy.org/?p=haproxy.git%3Ba=commit%3Bh=58df5aea0a0c926b2238f65908f5e9f83d1cca25
- https://lists.debian.org/debian-lts-announce/2022/05/msg00045.html
- https://usn.ubuntu.com/3858-1/
- http://www.securityfocus.com/bid/106280
- https://access.redhat.com/errata/RHBA-2019:0326
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2019:1436
