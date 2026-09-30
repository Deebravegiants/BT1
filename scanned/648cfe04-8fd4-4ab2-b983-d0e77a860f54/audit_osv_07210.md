# [H] BIT-odoo-2021-44476

## Summary
Severity: High
Advisory: BIT-odoo-2021-44476
Aliases: CVE-2021-44476
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-odoo-2021-44476
Type: osv

## Affected
- Bitnami: `odoo` — affected >=0 <15.0.1

## Details
A sandboxing issue in Odoo Community 15.0 and earlier and Odoo Enterprise 15.0 and earlier allows authenticated administrators to read local files on the server, including sensitive configuration files.

## References
- https://github.com/odoo/odoo/issues/107684
- https://www.debian.org/security/2023/dsa-5399
- https://nvd.nist.gov/vuln/detail/CVE-2021-44476
