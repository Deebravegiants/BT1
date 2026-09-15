# [M] rsync 3.2.5 < 3.5.0 Heap Out-of-Bounds Write via files-from Entry

## Summary
Severity: Medium
Advisory: CVE-2026-70461
Aliases: GHSA-jhxm-j4mq-3fj4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-70461
Type: osv

## Details
rsync 3.2.5 before 3.5.0 contains a heap out-of-bounds write vulnerability that allows remote unauthenticated attackers to write one attacker-controlled byte past the end of a heap allocation by supplying a crafted files-from entry. Attackers can trigger the vulnerability against a read-only rsync daemon module by providing a files-from entry containing both an interior and trailing backslash, causing the add_implied_include() function to under-count the trailing backslash when sizing the destination buffer.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70461.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-jhxm-j4mq-3fj4
- https://nvd.nist.gov/vuln/detail/CVE-2026-70461
- https://www.vulncheck.com/advisories/rsync-heap-out-of-bounds-write-via-files-from-entry
- https://github.com/RsyncProject/rsync
