# [C] UNA CMS 9.0.0-RC1 - 14.0.0-RC4 PHP Object Injection

## Summary
Severity: Critical
Advisory: CVE-2025-66571
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-66571
Type: osv

## Details
UNA CMS versions 9.0.0-RC1 - 14.0.0-RC4 contain a PHP object injection vulnerability in BxBaseMenuSetAclLevel.php where the profile_id POST parameter is passed to PHP unserialize() without proper handling, allowing remote, unauthenticated attackers to inject arbitrary PHP objects and potentially write and execute arbitrary PHP code.

## References
- https://unacms.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66571.json
- https://karmainsecurity.com/KIS-2025-01
- https://nvd.nist.gov/vuln/detail/CVE-2025-66571
- https://www.vulncheck.com/advisories/una-cms-900-rc1-1400-rc4-php-object-injection
- https://github.com/unacms/una
- https://www.exploit-db.com/exploits/52139
