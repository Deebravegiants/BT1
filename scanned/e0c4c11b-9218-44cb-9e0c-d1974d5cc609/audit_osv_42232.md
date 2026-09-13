# [M] sysPass 3.2.11 Missing Authorization via PublicLinkController Account Decryption

## Summary
Severity: Medium
Advisory: CVE-2026-65710
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-65710
Type: osv

## Details
sysPass through version 3.2.11 contains a missing authorization vulnerability that allows authenticated users with the PUBLICLINK_CREATE profile flag to trigger unauthorized decryption and persistent storage of any vault account's password by exploiting the absence of AccountAcl checks in the public link creation flow. Attackers can invoke the saveCreateFromAccountAction endpoint to cause AccountService::getDataForLink to load arbitrary target accounts without AccountFilterUser restrictions, decrypt credentials using the session master key, and serialize cleartext passwords into Vault storage on the PublicLink database row, enabling subsequent unauthenticated retrieval if the generated link hash is recovered.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65710.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65710
- https://www.vulncheck.com/advisories/syspass-missing-authorization-via-publiclinkcontroller-account-decryption
- https://github.com/nuxsmin/sysPass
- https://github.com/Caycon/cve-advisories/blob/main/2026/sysPass/CVE-2026-65710.md
