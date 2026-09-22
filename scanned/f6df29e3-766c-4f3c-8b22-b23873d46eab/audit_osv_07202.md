# [H] BIT-odoo-2021-23178

## Summary
Severity: High
Advisory: BIT-odoo-2021-23178
Aliases: CVE-2021-23178
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-odoo-2021-23178
Type: osv

## Affected
- Bitnami: `odoo` — affected >=0 <15.0.1

## Details
Improper access control in Odoo Community 15.0 and earlier and Odoo Enterprise 15.0 and earlier allows attackers to validate online payments with a tokenized payment method that belongs to another user, causing the victim's payment method to be charged instead.

## References
- https://github.com/odoo/odoo/issues/107690
- https://www.debian.org/security/2023/dsa-5399
- https://nvd.nist.gov/vuln/detail/CVE-2021-23178
