# [M] rsync 3.2.3 < 3.5.0 Out-of-Bounds Write via parse_size_arg()

## Summary
Severity: Medium
Advisory: CVE-2026-70457
Aliases: GHSA-pg7g-xqmr-xpfh
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-70457
Type: osv

## Details
rsync 3.2.3 before 3.5.0 contains an out-of-bounds write in parse_size_arg() where the return value of snprintf() is used directly as an index into a .bss-segment array without bounds checking. When snprintf truncates the formatted size string, the return value equals the number of characters that would have been written including the truncated portion, and this value may exceed the array length. The subsequent indexed write targets memory outside the intended array bounds, corrupting .bss memory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70457.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-pg7g-xqmr-xpfh
- https://nvd.nist.gov/vuln/detail/CVE-2026-70457
- https://www.vulncheck.com/advisories/rsync-out-of-bounds-write-via-parse-size-arg
- https://github.com/RsyncProject/rsync
