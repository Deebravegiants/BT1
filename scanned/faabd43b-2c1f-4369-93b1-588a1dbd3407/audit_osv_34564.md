# [M] OpenPrinting CUPS vulnerable to stack based out-of-bound write

## Summary
Severity: Medium
Advisory: CVE-2025-61915
Aliases: GHSA-hxm8-vfpq-jrfc
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2025-11-29
Source: https://osv.dev/vulnerability/CVE-2025-61915
Type: osv

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. Prior to version 2.4.15, a user in the lpadmin group can use the cups web ui to change the config and insert a malicious line. Then the cupsd process which runs as root will parse the new config and cause an out-of-bound write. This issue has been patched in version 2.4.15.

## References
- http://www.openwall.com/lists/oss-security/2025/11/27/5
- https://github.com/OpenPrinting/cups/releases/tag/v2.4.15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61915.json
- https://github.com/OpenPrinting/cups/security/advisories/GHSA-hxm8-vfpq-jrfc
- https://nvd.nist.gov/vuln/detail/CVE-2025-61915
- https://github.com/OpenPrinting/cups/commit/db8d560262c22a21ee1e55dfd62fa98d9359bcb0
