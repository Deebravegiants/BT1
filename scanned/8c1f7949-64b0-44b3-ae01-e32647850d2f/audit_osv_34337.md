# [M] OpenPrinting CUPS slow client can halt cupsd, leading to a possible DoS attack

## Summary
Severity: Medium
Advisory: CVE-2025-58436
Aliases: GHSA-8wpw-vfgm-qrrr
CVSS: 5.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-29
Source: https://osv.dev/vulnerability/CVE-2025-58436
Type: osv

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. Prior to version 2.4.15, a client that connects to cupsd but sends slow messages, e.g. only one byte per second, delays cupsd as a whole, such that it becomes unusable by other clients. This issue has been patched in version 2.4.15.

## References
- http://www.openwall.com/lists/oss-security/2025/11/27/4
- https://github.com/OpenPrinting/cups/releases/tag/v2.4.15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58436.json
- https://github.com/OpenPrinting/cups/security/advisories/GHSA-8wpw-vfgm-qrrr
- https://nvd.nist.gov/vuln/detail/CVE-2025-58436
- https://github.com/OpenPrinting/cups/commit/40008d76a001babbb9beb9d9d74b01a86fb6ddb4
