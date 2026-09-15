# [H] SuiteCRM has Authenticated Blind SQL Injection in OutboundEmail Legacy Functionality.

## Summary
Severity: High
Advisory: CVE-2026-29099
Aliases: GHSA-38rf-h37x-7767
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-29099
Type: osv

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. Prior to versions 7.15.1 and 8.9.3, the `retrieve()` function in `include/OutboundEmail/OutboundEmail.php` fails to properly neutralize the user controlled `$id` parameter. It is assumed that the function calling `retrieve()` will appropriately quote and sanitize the user input. However, two locations have been identified that can be reached through the `EmailUIAjax`  action on the `Email()` module where this is not the case. As such, it is possible for an authenticated user to perform SQL injection through the `retrieve()` function. This affects the latest major versions 7.15 and 8.9. As there do not appear to be restrictions on which tables can be called, it would be possible for an attacker to retrieve arbitrary information from the database, including user information and password hashes. Versions 7.15.1 and 8.9.3 patch the issue.

## References
- https://docs.suitecrm.com/admin/releases/7.15.x
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29099.json
- https://github.com/SuiteCRM/SuiteCRM/security/advisories/GHSA-38rf-h37x-7767
- https://nvd.nist.gov/vuln/detail/CVE-2026-29099
