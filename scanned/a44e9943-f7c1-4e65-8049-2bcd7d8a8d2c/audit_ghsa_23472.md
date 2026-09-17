# [C] MetalGenix GeniXCMS vulnerable to SQL Injection

## Summary
Severity: Critical
Advisory: GHSA-q4hw-62mx-q37w
CVE: CVE-2015-3933
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-q4hw-62mx-q37w
Type: github-advisory

## Affected
- Packagist: `genix/cms` — affected >=0

## Details
Multiple SQL injection vulnerabilities in inc/lib/User.class.php in MetalGenix GeniXCMS before 0.0.3-patch allow remote attackers to execute arbitrary SQL commands via the (1) email parameter or (2) userid parameter to register.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3933
- https://github.com/GeniXCMS/GeniXCMS
- https://github.com/semplon/GeniXCMS/releases/tag/v0.0.3-patch
- https://www.exploit-db.com/exploits/37363
