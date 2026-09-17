# [C] CVE-2017-5879

## Summary
Severity: Critical
Advisory: CVE-2017-5879
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-06
Source: https://osv.dev/vulnerability/CVE-2017-5879
Type: osv

## Details
An issue was discovered in Exponent CMS 2.4.1. This is a blind SQL injection that can be exploited by un-authenticated users via an HTTP GET request and which can be used to dump database data out to a malicious server, using an out-of-band technique, such as select_loadfile(). The vulnerability affects source_selector.php and the following parameter: src.

## References
- http://www.securityfocus.com/bid/96039
- https://github.com/exponentcms/exponent-cms/issues/73
