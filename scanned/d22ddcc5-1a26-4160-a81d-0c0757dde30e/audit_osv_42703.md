# [M] rsync 3.0.1 < 3.5.0 Heap Out-of-Bounds Write via read_args()

## Summary
Severity: Medium
Advisory: CVE-2026-70456
Aliases: GHSA-78jc-79jv-v6rw
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-70456
Type: osv

## Details
rsync 3.0.1 before 3.5.0 contains an out-of-bounds write vulnerability in the read_args() function that allows a malicious sender to corrupt adjacent heap memory by sending a crafted argument list. When the argument count causes the argv allocation to be exactly full, the trailing NULL terminator is written one slot beyond the allocation boundary, corrupting adjacent heap memory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70456.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-78jc-79jv-v6rw
- https://nvd.nist.gov/vuln/detail/CVE-2026-70456
- https://www.vulncheck.com/advisories/rsync-heap-out-of-bounds-write-via-read-args
- https://github.com/RsyncProject/rsync
