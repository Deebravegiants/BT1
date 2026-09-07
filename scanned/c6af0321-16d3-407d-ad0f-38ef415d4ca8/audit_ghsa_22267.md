# [M] ws-xmlrpc DoS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r2pg-w96p-pcpj
CVE: CVE-2016-5004
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-r2pg-w96p-pcpj
Type: github-advisory

## Affected
- Maven: `org.apache.xmlrpc:xmlrpc-common` — affected >=0

## Details
The Content-Encoding HTTP header feature in ws-xmlrpc 3.1.3 as used in Apache Archiva allows remote attackers to cause a denial of service (resource consumption) by decompressing a large file containing zeroes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5004
- https://github.com/0ang3el/unsafe-xmlrpc
- https://web.archive.org/web/20160716070844/http://www.securitytracker.com/id/1036294
- https://web.archive.org/web/20171111065719/http://www.securityfocus.com/bid/91736
- https://web.archive.org/web/20171114185236/https://0ang3el.blogspot.in/2016/07/beware-of-ws-xmlrpc-library-in-your.html
- http://www.openwall.com/lists/oss-security/2016/07/12/5
