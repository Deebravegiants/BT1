# [M] Authenticated XSS in "Publish Key" Field Allowing Unauthorized Administrator User Creation in SuiteCRM

## Summary
Severity: Medium
Advisory: BIT-suitecrm-2024-50335
Aliases: CVE-2024-50335, GHSA-8rw6-g96j-3w7m
Ecosystem: Bitnami
Published: 2024-11-07
Source: https://osv.dev/vulnerability/BIT-suitecrm-2024-50335
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=8.0.0 <8.7.1

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. The "Publish Key" field in SuiteCRM's Edit Profile page is vulnerable to Reflected Cross-Site Scripting (XSS), allowing an attacker to inject malicious JavaScript code. This can be exploited to steal CSRF tokens and perform unauthorized actions, such as creating new administrative users without proper authentication. The vulnerability arises due to insufficient input validation and sanitization of the Publish Key field within the SuiteCRM application. When an attacker injects a malicious script, it gets executed within the context of an authenticated user's session. The injected script (o.js) then leverages the captured CSRF token to forge requests that create new administrative users, effectively compromising the integrity and security of the CRM instance. This issue has been addressed in versions 7.14.6 and 8.7.1. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/salesagility/SuiteCRM/security/advisories/GHSA-8rw6-g96j-3w7m
- https://nvd.nist.gov/vuln/detail/CVE-2024-50335
