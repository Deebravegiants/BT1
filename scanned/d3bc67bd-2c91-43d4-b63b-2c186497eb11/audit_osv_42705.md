# [M] rsync 3.0.0 < 3.5.0 Out-of-Bounds Write via FLAG_HLINKED Handling

## Summary
Severity: Medium
Advisory: CVE-2026-70458
Aliases: GHSA-gg3m-4m9m-268h
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-70458
Type: osv

## Details
rsync 3.0.0 before 3.5.0 contains an out-of-bounds write vulnerability that allows attackers to corrupt memory by triggering HLINK_BUMP processing on file entries with the FLAG_HLINKED flag set while the hard-link preservation option is inactive. Attackers can exploit the missing F_SUM field in the file_struct layout to access memory past the end of the allocated structure, corrupting adjacent heap or stack data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70458.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-gg3m-4m9m-268h
- https://nvd.nist.gov/vuln/detail/CVE-2026-70458
- https://www.vulncheck.com/advisories/rsync-out-of-bounds-write-via-flag-hlinked-handling
- https://github.com/RsyncProject/rsync
