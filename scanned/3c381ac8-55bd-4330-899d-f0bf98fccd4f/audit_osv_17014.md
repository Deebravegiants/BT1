# [M] CVE-2020-11098

## Summary
Severity: Medium
Advisory: CVE-2020-11098
Aliases: GHSA-jr57-f58x-hjmv
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2020-06-22
Source: https://osv.dev/vulnerability/CVE-2020-11098
Type: osv

## Details
In FreeRDP before version 2.1.2, there is an out-of-bound read in glyph_cache_put. This affects all FreeRDP clients with `+glyph-cache` option enabled This is fixed in version 2.1.2.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6Y35HBHG2INICLSGCIKNAR7GCXEHQACQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XOZLH35OJWIQLM7FYDXAP2EAUBDXE76V/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00080.html
- http://www.freerdp.com/2020/06/22/2_1_2-released
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-jr57-f58x-hjmv
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://usn.ubuntu.com/4481-1/
- https://github.com/FreeRDP/FreeRDP/commit/c0fd449ec0870b050d350d6d844b1ea6dad4bc7d
