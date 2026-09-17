# [C] SuiteCRM Vulnerable to Remote Code Execution via Module Loader Package Scanner Bypass

## Summary
Severity: Critical
Advisory: CVE-2026-29103
Aliases: GHSA-5jjq-9qch-9rg7
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-29103
Type: osv

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. A Critical Remote Code Execution (RCE) vulnerability exists in SuiteCRM 7.15.0 and 8.9.2, allowing authenticated administrators to execute arbitrary system commands. This vulnerability is a direct Patch Bypass of CVE-2024-49774. Although the vendor attempted to fix the issue in version 7.14.5, the underlying flaw in ModuleScanner.php regarding PHP token parsing remains. The scanner incorrectly resets its internal state ($checkFunction flag) when encountering any single-character token (such as =, ., or ;). This allows attackers to hide dangerous function calls (e.g., system(), exec()) using variable assignments or string concatenation, completely evading the MLP security controls. Versions 7.15.1 and 8.9.3 patch the issue.

## References
- https://docs.suitecrm.com/admin/releases/7.15.x
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29103.json
- https://github.com/SuiteCRM/SuiteCRM/security/advisories/GHSA-5jjq-9qch-9rg7
- https://nvd.nist.gov/vuln/detail/CVE-2026-29103
