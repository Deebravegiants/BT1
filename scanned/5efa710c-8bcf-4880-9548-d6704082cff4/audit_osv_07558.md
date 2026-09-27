# [H] ModuleScanner flaws in SuiteCRM

## Summary
Severity: High
Advisory: BIT-suitecrm-2024-49774
Aliases: CVE-2024-49774, GHSA-9v56-vhp4-x227
Ecosystem: Bitnami
Published: 2024-11-07
Source: https://osv.dev/vulnerability/BIT-suitecrm-2024-49774
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=8.0.0 <8.7.1

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. SuiteCRM relies on the blacklist of functions/methods to prevent installation of malicious MLPs. But this checks can be bypassed with some syntax constructions. SuiteCRM uses token_get_all to parse PHP scripts and check the resulted AST against blacklists. But it doesn't take into account all scenarios. This issue has been addressed in versions 7.14.6 and 8.7.1. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/salesagility/SuiteCRM/security/advisories/GHSA-9v56-vhp4-x227
- https://nvd.nist.gov/vuln/detail/CVE-2024-49774
