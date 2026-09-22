# [M] TestLink 1.9.20 and prior Authenticated IDOR via attachmentdownload.php

## Summary
Severity: Medium
Advisory: CVE-2026-70561
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-70561
Type: osv

## Details
TestLink 1.9.20 and prior contains an insecure direct object reference vulnerability that allows any authenticated user, including low-privilege guest accounts, to read arbitrary attachments by supplying an integer attachment ID to the attachmentdownload.php handler without any project or role authorization check. Attackers can enumerate sequential integer IDs through the attachment download endpoint to retrieve file contents from private projects they have no membership in, bypassing the per-project access control model and exposing test specifications, requirements documents, execution evidence, and other sensitive uploaded files across the entire installation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70561.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-70561
- https://www.vulncheck.com/advisories/testlink-and-prior-authenticated-idor-via-attachmentdownload-php
- https://github.com/TestLinkOpenSourceTRMS/testlink-code
- https://github.com/geo-chen/oss/blob/main/testlink-code.md
