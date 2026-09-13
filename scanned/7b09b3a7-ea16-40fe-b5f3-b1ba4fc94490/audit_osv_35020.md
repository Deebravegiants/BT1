# [C] WBCE CMS has Weak Random Number Generator in Password Generation Function

## Summary
Severity: Critical
Advisory: CVE-2025-67504
Aliases: GHSA-76gj-pmvx-jcc6
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2025-67504
Type: osv

## Details
WBCE CMS is a content management system. Versions 1.6.4 and below use function GenerateRandomPassword() to create passwords using PHP's rand(). rand() is not cryptographically secure, which allows password sequences to be predicted or brute-forced. This can lead to user account compromise or privilege escalation if these passwords are used for new accounts or password resets. The vulnerability is fixed in version 1.6.5.

## References
- https://cwe.mitre.org/data/definitions/338.html
- https://github.com/WBCE/WBCE_CMS/releases/tag/1.6.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67504.json
- https://github.com/WBCE/WBCE_CMS/security/advisories/GHSA-76gj-pmvx-jcc6
- https://nvd.nist.gov/vuln/detail/CVE-2025-67504
- https://github.com/WBCE/WBCE_CMS/commit/5d59fe021a5c6e469b1bf192b72ca652e54278f6
