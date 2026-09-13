# [M] Path traversal in jefferson

## Summary
Severity: Medium
Advisory: CVE-2023-0592
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2023-01-31
Source: https://osv.dev/vulnerability/CVE-2023-0592
Type: osv

## Details
A path traversal vulnerability affects jefferson's JFFS2 filesystem extractor. By crafting malicious JFFS2 files, attackers could force jefferson to write outside of the extraction directory.This issue affects jefferson: before 0.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0592.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0592
- https://onekey.com/blog/security-advisory-remote-command-execution-in-binwalk/
- https://github.com/sviehb/jefferson/commit/971aca1a8b3b9f4fcb4674fa9621d3349195cdc6
- https://github.com/sviehb/jefferson
