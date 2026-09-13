# [M] rsync < 3.5.0 Arbitrary File Deletion via Malicious File List

## Summary
Severity: Medium
Advisory: CVE-2026-53789
Aliases: GHSA-fxwg-7hmf-xh5q
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-53789
Type: osv

## Details
rsync before 3.5.0 contains an improper path handling vulnerability that allows a malicious sender to expand the scope of --delete operations beyond the intended destination subtree by sending a crafted file list that causes rsync to reclassify implied parent directory entries or treat synthetic paths as the transfer root. Attackers can exploit multiple variants including implied parent reclassification, synthetic root path construction, legacy protocol behavior below version 30, and non-directory root handling to cause the receiver to delete files outside the authorized destination directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53789.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-fxwg-7hmf-xh5q
- https://nvd.nist.gov/vuln/detail/CVE-2026-53789
- https://www.vulncheck.com/advisories/rsync-arbitrary-file-deletion-via-malicious-file-list
- https://github.com/RsyncProject/rsync
