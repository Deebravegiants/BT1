# [M] CVE-2021-3622

## Summary
Severity: Medium
Advisory: CVE-2021-3622
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2021-12-23
Source: https://osv.dev/vulnerability/CVE-2021-3622
Type: osv

## Details
A flaw was found in the hivex library. This flaw allows an attacker to input a specially crafted Windows Registry (hive) file, which would cause hivex to recursively call the _get_children() function, leading to a stack overflow. The highest threat from this vulnerability is to system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/S35TVTAPHORSUIFYNFBHKLQRPVFUPXBE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/USD4OEV6L3RPHE32V2MJ4JPFBODINWSU/
- https://bugzilla.redhat.com/show_bug.cgi?id=1975489
- https://github.com/libguestfs/hivex/commit/771728218dac2fbf6997a7e53225e75a4c6b7255
- https://listman.redhat.com/archives/libguestfs/2021-August/msg00002.html
