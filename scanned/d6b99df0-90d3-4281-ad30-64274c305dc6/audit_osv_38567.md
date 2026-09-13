# [M] FreeScout's Customer AJAX Create Modifies Hidden Existing Customer

## Summary
Severity: Medium
Advisory: CVE-2026-40590
Aliases: GHSA-wjw4-8xg6-342m
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40590
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.214, the Change Customer modal exposes a “Create a new customer” flow via POST /customers/ajax with action=create. Under limited visibility, the endpoint drops unique-email validation. If the supplied email already belongs to a hidden customer, Customer::create() reuses that hidden customer object and fills empty profile fields from attacker-controlled input. Version 1.8.214 fixes the vulnerability.

## References
- https://github.com/freescout-help-desk/freescout/releases/tag/1.8.214
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40590.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-wjw4-8xg6-342m
- https://nvd.nist.gov/vuln/detail/CVE-2026-40590
- https://github.com/freescout-help-desk/freescout/commit/b3d7611e6e173ed8a5e525b791deb6b32cf1ce62
