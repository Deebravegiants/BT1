# [H] rsync < 3.5.0 Arbitrary File Write via --temp-dir/--link-dest

## Summary
Severity: High
Advisory: CVE-2026-53795
Aliases: GHSA-m9vj-637x-v6pq
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-53795
Type: osv

## Details
rsync before 3.5.0 contains an arbitrary file write vulnerability that allows attackers to write files outside the intended destination tree by specifying an absolute path via --temp-dir or --link-dest options. The rename-confinement logic is bypassed when these options resolve to paths outside the destination tree, enabling attacker-controlled values to write files to arbitrary locations accessible to the rsync process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53795.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-m9vj-637x-v6pq
- https://nvd.nist.gov/vuln/detail/CVE-2026-53795
- https://www.vulncheck.com/advisories/rsync-arbitrary-file-write-via-temp-dir-link-dest
- https://github.com/RsyncProject/rsync
