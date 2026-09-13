# [M] CVE-2019-14824

## Summary
Severity: Medium
Advisory: CVE-2019-14824
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-11-08
Source: https://osv.dev/vulnerability/CVE-2019-14824
Type: osv

## Details
A flaw was found in the 'deref' plugin of 389-ds-base where it could use the 'search' permission to display attribute values. In some configurations, this could allow an authenticated attacker to view private attributes, such as password hashes.

## References
- https://lists.debian.org/debian-lts-announce/2023/04/msg00026.html
- https://access.redhat.com/errata/RHSA-2019:3981
- https://access.redhat.com/errata/RHSA-2020:0464
- https://lists.debian.org/debian-lts-announce/2019/11/msg00036.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14824
