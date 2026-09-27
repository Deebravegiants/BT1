# [H] BIT-suitecrm-2020-15301

## Summary
Severity: High
Advisory: BIT-suitecrm-2020-15301
Aliases: CVE-2020-15301
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-suitecrm-2020-15301
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=0 <7.11.14

## Details
SuiteCRM through 7.11.13 allows CSV Injection via registration fields in the Accounts, Contacts, Opportunities, and Leads modules. These fields are mishandled during a Download Import File Template operation.

## References
- https://www.wizlynxgroup.com/security-research-advisories/vuln/WLX-2020-010
- https://nvd.nist.gov/vuln/detail/CVE-2020-15301
