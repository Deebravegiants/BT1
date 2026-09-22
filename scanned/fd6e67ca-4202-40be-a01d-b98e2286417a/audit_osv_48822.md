# [H] CVE-2018-14648

## Summary
Severity: High
Advisory: CVE-2018-14648
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-28
Source: https://osv.dev/vulnerability/CVE-2018-14648
Type: osv

## Details
A flaw was found in 389 Directory Server. A specially crafted search query could lead to excessive CPU consumption in the do_search() function. An unauthenticated attacker could use this flaw to provoke a denial of service.

## References
- https://access.redhat.com/errata/RHSA-2018:3127
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14648
- https://lists.debian.org/debian-lts-announce/2018/10/msg00015.html
- https://access.redhat.com/errata/RHSA-2018:3507
