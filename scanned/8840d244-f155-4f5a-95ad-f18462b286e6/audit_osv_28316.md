# [H] Redon-Hub has incorrect permissions on all admin related commands

## Summary
Severity: High
Advisory: CVE-2024-31442
Aliases: GHSA-3rx8-6453-7q26
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-08
Source: https://osv.dev/vulnerability/CVE-2024-31442
Type: osv

## Details
Redon Hub is a Roblox Product Delivery Bot, also known as a Hub. In all hubs before version 1.0.2, all commands are capable of being ran by all users, including admin commands. This allows users to receive products for free and delete/create/update products/tags/etc. The only non-affected command is `/products admin clear` as this was already programmed for bot owners only. All users should upgrade to version 1.0.2 to receive a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31442.json
- https://github.com/Redon-Tech/Redon-Hub/security/advisories/GHSA-3rx8-6453-7q26
- https://nvd.nist.gov/vuln/detail/CVE-2024-31442
- https://github.com/Redon-Tech/Redon-Hub/commit/38cb7c08d4d890e8a1badadbd46f459f06e3cdcd
