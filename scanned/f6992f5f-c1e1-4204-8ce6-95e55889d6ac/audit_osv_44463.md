# [M] parsedmarc < 11.0.1 Zip Bomb DoS via Compressed Email Attachments

## Summary
Severity: Medium
Advisory: CVE-2026-82520
Aliases: GHSA-43qf-f35w-2x4r
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-82520
Type: osv

## Details
parsedmarc before 11.0.1 decompresses gzip and ZIP attachments in a single unbounded read with no limit on decompressed output size. Because parsedmarc automatically processes incoming DMARC report emails without user interaction, an unauthenticated remote attacker can send a crafted email with a highly compressed attachment to the monitored mailbox, causing the parsedmarc process to allocate memory proportional to the uncompressed size and exhaust available RAM.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82520.json
- https://github.com/domainaware/parsedmarc/security/advisories/GHSA-43qf-f35w-2x4r
- https://nvd.nist.gov/vuln/detail/CVE-2026-82520
- https://www.vulncheck.com/advisories/parsedmarc-zip-bomb-dos-via-compressed-email-attachments
- https://github.com/domainaware/parsedmarc/releases/tag/11.0.1
- https://github.com/domainaware/parsedmarc
