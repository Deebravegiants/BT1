# [C] CVE-2017-5344

## Summary
Severity: Critical
Advisory: CVE-2017-5344
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-17
Source: https://osv.dev/vulnerability/CVE-2017-5344
Type: osv

## Details
An issue was discovered in dotCMS through 3.6.1. The findChildrenByFilter() function which is called by the web accessible path /categoriesServlet performs string interpolation and direct SQL query execution. SQL quote escaping and a keyword blacklist were implemented in a new class, SQLUtil (main/java/com/dotmarketing/common/util/SQLUtil.java), as part of the remediation of CVE-2016-8902; however, these can be overcome in the case of the q and inode parameters to the /categoriesServlet path. Overcoming these controls permits a number of blind boolean SQL injection vectors in either parameter. The /categoriesServlet web path can be accessed remotely and without authentication in a default dotCMS deployment.

## References
- http://www.securityfocus.com/bid/96259
- https://www.exploit-db.com/exploits/41377/
- http://dotcms.com/security/SI-39
- http://seclists.org/fulldisclosure/2017/Feb/34
- https://github.com/xdrr/webapp-exploits/blob/master/vendors/dotcms/2017.01.blind-sqli/dotcms-dump.sh
