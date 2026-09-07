# [H] Apache XML-RPC XXE Vulnerability

## Summary
Severity: High
Advisory: GHSA-wp35-6jqv-r33m
CVE: CVE-2016-5002
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-wp35-6jqv-r33m
Type: github-advisory

## Affected
- Maven: `org.apache.xmlrpc:xmlrpc` — affected >=0

## Details
XML external entity (XXE) vulnerability in the Apache XML-RPC (aka ws-xmlrpc) library 3.1.3, as used in Apache Archiva, allows remote attackers to conduct server-side request forgery (SSRF) attacks via a crafted DTD.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5002
- https://access.redhat.com/errata/RHSA-2018:3768
- https://exchange.xforce.ibmcloud.com/vulnerabilities/115042
- https://security.gentoo.org/glsa/202401-26
- https://web.archive.org/web/20210123151805/http://www.securityfocus.com/bid/91736
- https://web.archive.org/web/20211021044107/http://www.securitytracker.com/id/1036294
- https://web.archive.org/web/20230520164025/https://0ang3el.blogspot.com/2016/07/beware-of-ws-xmlrpc-library-in-your.html
- http://www.openwall.com/lists/oss-security/2016/07/12/5
- http://www.securityfocus.com/bid/91736
- http://www.securitytracker.com/id/1036294
