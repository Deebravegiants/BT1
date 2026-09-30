# [H] CVE-2026-56135

## Summary
Severity: High
Advisory: CVE-2026-56135
Aliases: GHSA-c9qg-fh4v-mq8r
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-56135
Type: osv

## Details
In NTFS-3G through 2026.2.25, a heap-based buffer overflow exists in the function build_inherited_id() in libntfs-3g/security.c that allows an attacker to corrupt heap memory in the SUID-root ntfs-3g binary by crafting a malicious NTFS image. The overflow is triggered by creating a file in a crafted directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56135.json
- https://github.com/tuxera/ntfs-3g/security/advisories/GHSA-c9qg-fh4v-mq8r
- https://nvd.nist.gov/vuln/detail/CVE-2026-56135
