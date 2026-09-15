# [H] RCE in ModuleBuilder in SuiteCRM

## Summary
Severity: High
Advisory: BIT-suitecrm-2024-50333
Aliases: CVE-2024-50333, GHSA-qrv6-3q86-qv89
Ecosystem: Bitnami
Published: 2024-11-07
Source: https://osv.dev/vulnerability/BIT-suitecrm-2024-50333
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=8.0.0 <8.7.1

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. User input is not validated and is written to the filesystem. The ParserLabel::addLabels() function can be used to write attacker-controlled data into the custom language file that will be included at the runtime. This issue has been addressed in versions 7.14.6 and 8.7.1. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/salesagility/SuiteCRM/security/advisories/GHSA-qrv6-3q86-qv89
- https://nvd.nist.gov/vuln/detail/CVE-2024-50333
