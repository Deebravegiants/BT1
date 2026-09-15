# [H] BIT-odoo-2021-44460

## Summary
Severity: High
Advisory: BIT-odoo-2021-44460
Aliases: CVE-2021-44460
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-odoo-2021-44460
Type: osv

## Affected
- Bitnami: `odoo` — affected >=0 <13.0.1

## Details
Improper access control in Odoo Community 13.0 and earlier and Odoo Enterprise 13.0 and earlier allows users with deactivated accounts to access the system with the deactivated account and any permission it still holds, via crafted RPC requests.

## References
- https://github.com/odoo/odoo/issues/107685
- https://nvd.nist.gov/vuln/detail/CVE-2021-44460
