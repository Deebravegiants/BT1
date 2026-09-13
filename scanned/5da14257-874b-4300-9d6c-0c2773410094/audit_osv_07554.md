# [H] SuiteCRM authenticated RCE using connectors

## Summary
Severity: High
Advisory: BIT-suitecrm-2024-36418
Aliases: CVE-2024-36418, GHSA-mfj5-37v4-vh5w
Ecosystem: Bitnami
Published: 2024-06-12
Source: https://osv.dev/vulnerability/BIT-suitecrm-2024-36418
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=8.0.0 <8.6.1

## Details
SuiteCRM is an open-source Customer Relationship Management (CRM) software application. Prior to versions 7.14.4 and 8.6.1, a vulnerability in connectors allows an authenticated user to perform a remote code execution attack. Versions 7.14.4 and 8.6.1 contain a fix for this issue.

## References
- https://github.com/salesagility/SuiteCRM/security/advisories/GHSA-mfj5-37v4-vh5w
- https://nvd.nist.gov/vuln/detail/CVE-2024-36418
