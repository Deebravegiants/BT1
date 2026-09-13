# [M] CVE-2017-7388

## Summary
Severity: Medium
Advisory: CVE-2017-7388
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2017-04-01
Source: https://osv.dev/vulnerability/CVE-2017-7388
Type: osv

## Details
A Cross-Site Scripting (XSS) was discovered in 'wallacepos v1.4.1'. The vulnerability exists due to insufficient filtration of user-supplied data (token) passed to the 'wallacepos-master/myaccount/resetpassword.php' URL. An attacker could execute arbitrary HTML and script code in a browser in the context of the vulnerable website.

## References
- http://www.securityfocus.com/bid/97316
- https://github.com/micwallace/wallacepos/issues/84
