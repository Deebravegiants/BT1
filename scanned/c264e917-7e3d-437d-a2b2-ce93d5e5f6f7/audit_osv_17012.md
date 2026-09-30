# [M] CVE-2020-11096

## Summary
Severity: Medium
Advisory: CVE-2020-11096
Aliases: GHSA-mjw7-3mq2-996x
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2020-06-22
Source: https://osv.dev/vulnerability/CVE-2020-11096
Type: osv

## Details
In FreeRDP before version 2.1.2, there is a global OOB read in update_read_cache_bitmap_v3_order. As a workaround, one can disable bitmap cache with -bitmap-cache (default). This is fixed in version 2.1.2.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6Y35HBHG2INICLSGCIKNAR7GCXEHQACQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XOZLH35OJWIQLM7FYDXAP2EAUBDXE76V/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00080.html
- http://www.freerdp.com/2020/06/22/2_1_2-released
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-mjw7-3mq2-996x
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://usn.ubuntu.com/4481-1/
- https://github.com/FreeRDP/FreeRDP/commit/b8beb55913471952f92770c90c372139d78c16c0
