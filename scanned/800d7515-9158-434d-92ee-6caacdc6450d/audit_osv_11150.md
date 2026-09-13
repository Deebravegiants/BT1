# [M] CVE-2017-6396

## Summary
Severity: Medium
Advisory: CVE-2017-6396
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2017-03-02
Source: https://osv.dev/vulnerability/CVE-2017-6396
Type: osv

## Details
An issue was discovered in WPO-Foundation WebPageTest 3.0. The vulnerability exists due to insufficient filtration of user-supplied data passed to the "webpagetest-master/www/compare-cf.php" URL. An attacker could execute arbitrary HTML and script code in a browser in the context of the vulnerable website.

## References
- http://www.securityfocus.com/bid/96553
- https://github.com/MarkLee131/awesome-web-pocs/blob/main/CVE-2017-6396.md
- https://github.com/WPO-Foundation/webpagetest/issues/820
