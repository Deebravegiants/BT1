# [M] barebox ext4 Directory Parsing Infinite Loop Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-34962
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-34962
Type: osv

## Details
barebox version prior to 2026.04.0 contains a denial-of-service vulnerability in ext4 directory parsing in fs/ext4/ext4_common.c where the ext4fs_iterate_dir() function fails to validate that directory entry length values are non-zero. Attackers can supply a malicious ext4 filesystem image with a crafted directory entry containing a direntlen value of 0 to cause an infinite loop during directory listing or path resolution, resulting in the boot process hanging indefinitely.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34962.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-34962
- https://www.vulncheck.com/advisories/barebox-ext4-directory-parsing-infinite-loop-denial-of-service
- https://github.com/barebox/barebox/releases/tag/v2026.04.0
- https://github.com/barebox/barebox
- https://y637f9qq2x.com/posts/barebox-sandbox-vulns/
