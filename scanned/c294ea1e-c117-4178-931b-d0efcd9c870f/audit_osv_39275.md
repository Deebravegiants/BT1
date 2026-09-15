# [M] libzypp .repo files can have an optional path which can lead to path traversal attacks

## Summary
Severity: Medium
Advisory: CVE-2026-44942
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-44942
Type: osv

## Details
A path traversal in handling the "path" component of .repo files processed by libzypp before 17.38.13 in the 17.x series, or before 16.22.19 could be used by attackers to fill directories on the system outside of the zypp cache with content.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44942.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-44942
- https://www.suse.com/security/cve/CVE-2026-44942.html
- https://bugzilla.suse.com/show_bug.cgi?id=1267874
- https://github.com/opensuse/libzypp
