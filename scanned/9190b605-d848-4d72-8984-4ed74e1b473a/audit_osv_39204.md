# [H] Saleor: Account pre-hijacking vulnerability due to unverified anonymous order merge

## Summary
Severity: High
Advisory: CVE-2026-44472
Aliases: GHSA-6whj-8p3f-2xqp
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-44472
Type: osv

## Details
Saleor is an e-commerce platform. From 2.10.0rc1 until 3.21.67, 3.22.63, and 3.23.22, the account activation flow treats email verification as sufficient proof of account ownership and automatically associates anonymous commerce data with the newly activated account. An attacker can use accountRegister to create an account with a victim's email address before the victim registers. If the victim follows the activation link sent to that mailbox, Saleor activates the attacker-created account and saleor/graphql/account/mutations/account/confirm_account.py can merge anonymous orders and gift-card data for the same email address without requiring the account password or another authentication factor. The attacker can then access the merged order history and personal data, including names, addresses, and phone numbers. The patched supported lines disable automatic merging by default, while the redesigned 3.24.0 flow requires password confirmation before anonymous objects are linked. This issue is fixed in versions 3.21.67, 3.22.63, and 3.23.22.

## References
- https://github.com/saleor/saleor/releases/tag/3.21.67
- https://github.com/saleor/saleor/releases/tag/3.22.63
- https://github.com/saleor/saleor/releases/tag/3.23.22
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44472.json
- https://github.com/saleor/saleor/security/advisories/GHSA-6whj-8p3f-2xqp
- https://nvd.nist.gov/vuln/detail/CVE-2026-44472
- https://github.com/saleor/saleor/commit/299cdfb1a5737108b78b5c2c0d29b94f3b7331a2
- https://github.com/saleor/saleor/commit/42516727823cb74cb6b875070956debecf9ffdb8
- https://github.com/saleor/saleor/commit/5110542c164991384fa3c4f01983e8c76823ce0f
- https://github.com/saleor/saleor/commit/dc63e422afc9f6ce115d75f045886b01b4f13e2b
