# [H] wordexp with WRDE_REUSE and WRDE_APPEND may return uninitialized memory

## Summary
Severity: High
Advisory: CVE-2025-15281
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/CVE-2025-15281
Type: osv

## Details
Calling wordexp with WRDE_REUSE in conjunction with WRDE_APPEND in the GNU C Library version 2.0 to version 2.42 may cause the interface to return uninitialized memory in the we_wordv member, which on subsequent calls to wordfree may abort the process.

## References
- http://www.openwall.com/lists/oss-security/2026/01/20/3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/15xxx/CVE-2025-15281.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-15281
- https://sourceware.org/bugzilla/show_bug.cgi?id=33814
