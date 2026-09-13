# [M] CVE-2020-11095

## Summary
Severity: Medium
Advisory: CVE-2020-11095
Aliases: GHSA-563r-pvh7-4fw2
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L)
Published: 2020-06-22
Source: https://osv.dev/vulnerability/CVE-2020-11095
Type: osv

## Details
In FreeRDP before version 2.1.2, an out of bound reads occurs resulting in accessing a memory location that is outside of the boundaries of the static array PRIMARY_DRAWING_ORDER_FIELD_BYTES. This is fixed in version 2.1.2.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6Y35HBHG2INICLSGCIKNAR7GCXEHQACQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XOZLH35OJWIQLM7FYDXAP2EAUBDXE76V/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00080.html
- http://www.freerdp.com/2020/06/22/2_1_2-released
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-563r-pvh7-4fw2
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://usn.ubuntu.com/4481-1/
- https://github.com/FreeRDP/FreeRDP/commit/733ee3208306b1ea32697b356c0215180fc3f049
