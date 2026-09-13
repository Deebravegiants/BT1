# [H] CVE-2018-6029

## Summary
Severity: High
Advisory: CVE-2018-6029
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-01-23
Source: https://osv.dev/vulnerability/CVE-2018-6029
Type: osv

## Details
The copy function in application/admin/controller/Article.php in NoneCms 1.3.0 allows remote attackers to access the content of internal and external network resources via Server Side Request Forgery (SSRF), because URL validation only considers whether the URL contains the "csdn" substring.

## References
- http://blackwolfsec.cc/2018/01/23/Nonecms_ssrf/
