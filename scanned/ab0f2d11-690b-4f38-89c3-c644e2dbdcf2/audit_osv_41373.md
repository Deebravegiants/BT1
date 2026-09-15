# [M] Gumroad < 2026.07.06.2 - Insecure Direct Object Reference in PurchasesController

## Summary
Severity: Medium
Advisory: CVE-2026-59805
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-59805
Type: osv

## Details
Gumroad before 2026.07.06.2 contains a broken access control vulnerability in the PurchasesController that allows authenticated sellers to manipulate purchase access for other sellers' products by sending PUT requests to the revoke_access and undo_revoke_access actions without seller ownership validation. Attackers can modify the is_access_revoked status on arbitrary purchases to unauthorized revoke or restore buyer access to products they do not own.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59805.json
- https://github.com/antiwork/gumroad/releases/tag/v2026.07.06.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-59805
- https://www.vulncheck.com/advisories/gumroad-insecure-direct-object-reference-in-purchasescontroller
- https://github.com/antiwork/gumroad/pull/5731
- https://github.com/antiwork/gumroad/commit/e7fd0e610e73135ecf1aa07c197a36fa524832e1
- https://github.com/antiwork/gumroad
- https://github.com/antiwork/gumroad/issues/5725
