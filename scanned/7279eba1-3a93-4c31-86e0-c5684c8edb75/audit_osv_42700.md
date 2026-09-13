# [M] rsync < 3.5.0 Algorithmic Complexity DoS via hash_search()

## Summary
Severity: Medium
Advisory: CVE-2026-70453
Aliases: GHSA-8x5r-mjx8-83hv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-70453
Type: osv

## Details
rsync before 3.5.0 contains an algorithmic complexity vulnerability in the hash_search() function that allows a remote attacker to cause a denial of service by delivering a carefully constructed file list. A sender can exploit the quadratic-time worst-case behavior in hash lookups to exhaust receiver CPU resources with a modest number of crafted entries, causing a sustained denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70453.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-8x5r-mjx8-83hv
- https://nvd.nist.gov/vuln/detail/CVE-2026-70453
- https://www.vulncheck.com/advisories/rsync-algorithmic-complexity-dos-via-hash-search
- https://github.com/RsyncProject/rsync
