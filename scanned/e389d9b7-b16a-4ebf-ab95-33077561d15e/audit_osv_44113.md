# [M] rclone Archive Backend SquashFS Parser Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-79775
Aliases: GHSA-6jcg-q3wp-x2f4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-79775
Type: osv

## Details
rclone versions >= v1.72.0 and <= v1.74.4 (fixed in v1.75.0) contain multiple denial-of-service vulnerabilities in the archive backend's SquashFS parser, which relies on the github.com/diskfs/go-diskfs dependency. The parser fails to validate attacker-controlled superblock and metadata values before use. An attacker who can place or modify a SquashFS image in storage exposed through an rclone :archive: remote can craft a malicious image that triggers an integer division-by-zero panic (zero block size), an out-of-bounds slice panic (out-of-range inode metadata offset), or a non-progress CPU loop (truncated metadata stream). Variants 1 and 2 terminate the rclone process and, via 'rclone serve sftp', can crash the entire SFTP server; variant 3 causes sustained CPU consumption. Parsing is lazy, so a victim or remote client must address or descend into the malicious archive object to trigger it.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79775.json
- https://github.com/rclone/rclone/security/advisories/GHSA-6jcg-q3wp-x2f4
- https://nvd.nist.gov/vuln/detail/CVE-2026-79775
- https://www.vulncheck.com/advisories/rclone-archive-backend-squashfs-parser-denial-of-service
