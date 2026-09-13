# [H] CVE-2026-40706

## Summary
Severity: High
Advisory: CVE-2026-40706
Aliases: GHSA-4cwv-5285-63v9
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40706
Type: osv

## Details
In NTFS-3G 2022.10.3 before 2026.2.25, a heap buffer overflow exists in ntfs_build_permissions_posix() in acls.c that allows an attacker to corrupt heap memory in the SUID-root ntfs-3g binary by crafting a malicious NTFS image. The overflow is triggered on the READ path (stat, readdir, open) when processing a security descriptor with multiple ACCESS_DENIED ACEs containing WRITE_OWNER from distinct group SIDs.

## References
- http://www.openwall.com/lists/oss-security/2026/04/21/4
- https://github.com/tuxera/ntfs-3g/blob/d3ace19838ce37cfde55294e76841e6d2f393f9e/libntfs-3g/acls.c#L4011-L4027
- https://github.com/tuxera/ntfs-3g/releases/tag/2026.2.25
- https://lists.debian.org/debian-lts-announce/2026/04/msg00024.html
- https://www.openwall.com/lists/oss-security/2026/04/21/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40706.json
- https://github.com/tuxera/ntfs-3g/security/advisories/GHSA-4cwv-5285-63v9
- https://nvd.nist.gov/vuln/detail/CVE-2026-40706
