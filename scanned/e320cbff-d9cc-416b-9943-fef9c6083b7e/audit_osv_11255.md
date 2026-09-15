# [M] CVE-2017-6909

## Summary
Severity: Medium
Advisory: CVE-2017-6909
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-6909
Type: osv

## Details
An issue was discovered in Shimmie <= 2.5.1. The vulnerability exists due to insufficient filtration of user-supplied data (log) passed to the "shimmie2-master/ext/chatbox/history/index.php" URL. An attacker could execute arbitrary HTML and script code in a browser in the context of the vulnerable website.

## References
- http://www.securityfocus.com/bid/96932
- https://github.com/shish/shimmie2/issues/597
