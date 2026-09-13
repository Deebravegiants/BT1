# [C] ChurchCRM has an API Authentication Bypass

## Summary
Severity: Critical
Advisory: CVE-2026-39339
Aliases: GHSA-v3p2-mx78-pxhc
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-39339
Type: osv

## Details
ChurchCRM is an open-source church management system. Prior to 7.1.0, a  critical authentication bypass vulnerability in ChurchCRM's API middleware (ChurchCRM/Slim/Middleware/AuthMiddleware.php) allows unauthenticated attackers to access all protected API endpoints by including "api/public" anywhere in the request URL, leading to complete exposure of church member data and system information. This vulnerability is fixed in 7.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39339.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-v3p2-mx78-pxhc
- https://nvd.nist.gov/vuln/detail/CVE-2026-39339
