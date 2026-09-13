# [M] rsync < 3.5.0 Out-of-Bounds Read via Zero-Length Checksum Block

## Summary
Severity: Medium
Advisory: CVE-2026-53792
Aliases: GHSA-cg57-rp9g-56hw
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-53792
Type: osv

## Details
rsync before 3.5.0 contains an out-of-bounds read vulnerability in the sender-side block matching logic that allows a malicious receiver to trigger memory access before the start of an allocated buffer by sending a crafted checksum block with a length of zero. Attackers can send a specially crafted checksum set containing a zero-length block to cause a negative offset calculation during delta computation, resulting in an out-of-bounds read of file data buffer memory on the sender side.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53792.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-cg57-rp9g-56hw
- https://nvd.nist.gov/vuln/detail/CVE-2026-53792
- https://www.vulncheck.com/advisories/rsync-out-of-bounds-read-via-zero-length-checksum-block
- https://github.com/RsyncProject/rsync
