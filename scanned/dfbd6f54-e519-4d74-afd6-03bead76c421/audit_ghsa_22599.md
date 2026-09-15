# [H] AdaptCMS SQL Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-qrw3-mq8r-cq7q
CVE: CVE-2008-4524
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-qrw3-mq8r-cq7q
Type: github-advisory

## Affected
- Packagist: `adaptcms/adaptcms` — affected >=0

## Details
SQL injection vulnerability in the "Check User" feature (includes/check_user.php) in AdaptCMS Lite and AdaptCMS Pro 1.3 allows remote attackers to execute arbitrary SQL commands via the user_name parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-4524
- https://exchange.xforce.ibmcloud.com/vulnerabilities/45642
- https://github.com/adaptcms/AdaptCMS
- https://web.archive.org/web/20200228141415/http://www.securityfocus.com/bid/31557
- https://www.exploit-db.com/exploits/6662
- http://www.adaptcms.com/article/51/News/URGENT-AdaptCMS-13-Security-Fix-Released
