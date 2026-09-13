# [M] CVE-2017-5960

## Summary
Severity: Medium
Advisory: CVE-2017-5960
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2017-02-12
Source: https://osv.dev/vulnerability/CVE-2017-5960
Type: osv

## Details
An issue was discovered in Phalcon Eye through 0.4.1. The vulnerability exists due to insufficient filtration of user-supplied data in multiple HTTP GET parameters passed to the "phalconeye-master/public/external/pydio/plugins/editor.webodf/frame.php" URL. An attacker could execute arbitrary HTML and script code in a browser in the context of the vulnerable website.

## References
- http://www.securityfocus.com/bid/96201
- https://github.com/PhalconEye/phalconeye/issues/133
