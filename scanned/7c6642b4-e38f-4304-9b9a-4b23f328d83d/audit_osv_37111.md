# [M] Vim has Heap-based Buffer Overflow and OOB Read in :terminal

## Summary
Severity: Medium
Advisory: CVE-2026-28420
Aliases: GHSA-rvj2-jrf9-2phg
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-28420
Type: osv

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0076, a heap-based buffer overflow WRITE and an out-of-bounds READ exist in Vim's terminal emulator when processing maximum combining characters from Unicode supplementary planes. Version 9.2.0076 fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/02/27/9
- https://github.com/vim/vim/releases/tag/v9.2.0076
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28420.json
- https://github.com/vim/vim/security/advisories/GHSA-rvj2-jrf9-2phg
- https://nvd.nist.gov/vuln/detail/CVE-2026-28420
- https://github.com/vim/vim/commit/bb6de2105b160e729c34063
