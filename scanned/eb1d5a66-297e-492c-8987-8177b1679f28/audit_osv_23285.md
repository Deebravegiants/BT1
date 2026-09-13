# [C] CVE-2022-46887

## Summary
Severity: Critical
Advisory: CVE-2022-46887
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-19
Source: https://osv.dev/vulnerability/CVE-2022-46887
Type: osv

## Details
Multiple SQL injection vulnerabilities in NexusPHP before 1.7.33 allow remote attackers to execute arbitrary SQL commands via the conuser[] parameter in takeconfirm.php; the delcheater parameter in cheaterbox.php; or the usernw parameter in nowarn.php.

## References
- https://github.com/xiaomlove/nexusphp/releases/tag/v1.7.33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46887.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-46887
- https://www.surecloud.com/resources/blog/nexusphp-surecloud-security-review-identifies-authenticated-unauthenticated-vulnerabilities
