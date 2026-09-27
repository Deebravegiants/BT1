# [M] SolidInvoice's user invitation tokens have no expiry, allowing indefinite unauthorized company access via leaked or old invitation links

## Summary
Severity: Medium
Advisory: CVE-2026-61608
Aliases: GHSA-5gcp-fm29-jgrp
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-61608
Type: osv

## Details
SolidInvoice is an open-source invoicing platform. Prior to version 3.0.1, `UserInvitation` entities have no expiry timestamp. Invitation links mailed to users remain valid indefinitely, meaning a leaked, forwarded, or archived invitation email can be used at any time in the future to join a company or silently add a compromised email account to a company. Version 3.0.1 fixes the issue.

## References
- https://github.com/SolidInvoice/SolidInvoice/releases/tag/3.0.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61608.json
- https://github.com/SolidInvoice/SolidInvoice/security/advisories/GHSA-5gcp-fm29-jgrp
- https://nvd.nist.gov/vuln/detail/CVE-2026-61608
