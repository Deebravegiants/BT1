# [C] Apache XML-RPC vulnerable to Deserialization of Untrusted Data

## Summary
Severity: Critical
Advisory: GHSA-4gqp-296r-j5mq
CVE: CVE-2016-5003
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-4gqp-296r-j5mq
Type: github-advisory

## Affected
- Maven: `org.apache.xmlrpc:xmlrpc` — affected >=0

## Details
The Apache XML-RPC (aka ws-xmlrpc) library 3.1.3, as used in Apache Archiva, allows remote attackers to execute arbitrary code via a crafted serialized Java object in an <ex:serializable> element.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5003
- https://www.openwall.com/lists/oss-security/2020/01/24/2
- https://www.openwall.com/lists/oss-security/2020/01/16/1
- https://www.openwall.com/lists/oss-security/2016/07/12/5
- https://web.archive.org/web/20200227235226/http://www.securityfocus.com/bid/91738
- https://web.archive.org/web/20171111065719/http://www.securityfocus.com/bid/91736
- https://web.archive.org/web/20160716070844/http://www.securitytracker.com/id/1036294
- https://security.gentoo.org/glsa/202401-26
- https://exchange.xforce.ibmcloud.com/vulnerabilities/115043
- https://bugzilla.redhat.com/show_bug.cgi?id=1508123
- https://access.redhat.com/security/cve/CVE-2016-5003
- https://access.redhat.com/errata/RHSA-2018:3768
- https://access.redhat.com/errata/RHSA-2018:2317
- https://access.redhat.com/errata/RHSA-2018:1784
- https://access.redhat.com/errata/RHSA-2018:1780
- https://access.redhat.com/errata/RHSA-2018:1779
- https://0ang3el.blogspot.ru/2016/07/beware-of-ws-xmlrpc-library-in-your.html
- http://www.openwall.com/lists/oss-security/2016/07/12/5
- http://www.openwall.com/lists/oss-security/2020/01/16/1
- http://www.openwall.com/lists/oss-security/2020/01/24/2
