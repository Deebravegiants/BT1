# [C] CVE-2022-40357

## Summary
Severity: Critical
Advisory: CVE-2022-40357
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-20
Source: https://osv.dev/vulnerability/CVE-2022-40357
Type: osv

## Details
A security issue was discovered in Z-BlogPHP <= 1.7.2. A Server-Side Request Forgery (SSRF) vulnerability in the zb_users/plugin/UEditor/php/action_crawler.php file allows remote attackers to force the application to make arbitrary requests via injection of arbitrary URLs into the source parameter.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/40xxx/CVE-2022-40357.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-40357
- https://github.com/zblogcn/zblogphp/issues/336
