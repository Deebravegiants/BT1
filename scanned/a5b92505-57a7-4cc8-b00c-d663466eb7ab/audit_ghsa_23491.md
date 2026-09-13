# [C] PyWebDAV SQL Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-69vw-jfq7-935g
CVE: CVE-2011-0432
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-69vw-jfq7-935g
Type: github-advisory

## Affected
- PyPI: `pywebdav` — affected >=0 <0.9.4.1

## Details
Multiple SQL injection vulnerabilities in the `get_userinfo` method in the MySQLAuthHandler class in `DAVServer/mysqlauth.py` in PyWebDAV before 0.9.4.1 allow remote attackers to execute arbitrary SQL commands via the (1) user or (2) pw argument.  NOTE: some of these details are obtained from third party information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-0432
- https://bugzilla.redhat.com/show_bug.cgi?id=677718
- https://github.com/ashtons/pywebdav-iphone
- https://github.com/pypa/advisory-database/tree/main/vulns/pywebdav/PYSEC-2011-7.yaml
- https://web.archive.org/web/20110305233800/http://secunia.com/advisories/43571
- https://web.archive.org/web/20110321033933/http://secunia.com/advisories/43602
- https://web.archive.org/web/20110321055414/http://secunia.com/advisories/43703
- https://web.archive.org/web/20200228163209/http://www.securityfocus.com/bid/46655
- http://code.google.com/p/pywebdav/updates/list
- http://lists.fedoraproject.org/pipermail/package-announce/2011-March/055412.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-March/055413.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-March/055444.html
- http://pywebdav.googlecode.com/files/PyWebDAV-0.9.4.1.tar.gz
