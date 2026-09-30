# [H] BIT-odoo-2021-23186

## Summary
Severity: High
Advisory: BIT-odoo-2021-23186
Aliases: CVE-2021-23186
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-odoo-2021-23186
Type: osv

## Affected
- Bitnami: `odoo` — affected >=0 <15.0.1

## Details
A sandboxing issue in Odoo Community 15.0 and earlier and Odoo Enterprise 15.0 and earlier allows authenticated administrators to access and modify database contents of other tenants, in a multi-tenant system.

## References
- https://github.com/odoo/odoo/issues/107688
- https://www.debian.org/security/2023/dsa-5399
- https://nvd.nist.gov/vuln/detail/CVE-2021-23186
