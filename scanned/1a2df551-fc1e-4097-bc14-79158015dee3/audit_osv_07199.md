# [C] BIT-odoo-2020-29396

## Summary
Severity: Critical
Advisory: BIT-odoo-2020-29396
Aliases: CVE-2020-29396
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-odoo-2020-29396
Type: osv

## Affected
- Bitnami: `odoo` — affected >=11.0.0 <13.0.1

## Details
A sandboxing issue in Odoo Community 11.0 through 13.0 and Odoo Enterprise 11.0 through 13.0, when running with Python 3.6 or later, allows remote authenticated users to execute arbitrary code, leading to privilege escalation.

## References
- https://github.com/odoo/odoo/issues/63712
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-29396
