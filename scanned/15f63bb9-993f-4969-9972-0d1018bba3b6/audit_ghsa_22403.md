# [C] Apache MyFaces Trinidad Deserialization Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-x7rc-4gqw-3q6q
CVE: CVE-2016-5019
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-x7rc-4gqw-3q6q
Type: github-advisory

## Affected
- Maven: `org.apache.myfaces.trinidad:trinidad` — affected >=1.0.0
- Maven: `org.apache.myfaces.trinidad:trinidad` — affected >=1.2.0 <1.2.15
- Maven: `org.apache.myfaces.trinidad:trinidad` — affected >=2.0.0 <2.0.2
- Maven: `org.apache.myfaces.trinidad:trinidad` — affected >=2.1.0 <2.1.2

## Details
`CoreResponseStateManager` in Apache MyFaces Trinidad 1.0.0 through 1.0.13, 1.2.x before 1.2.15, 2.0.x before 2.0.2, and 2.1.x before 2.1.2 might allow attackers to conduct deserialization attacks via a crafted serialized viewstate string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5019
- https://github.com/apache/myfaces-trinidad
- https://issues.apache.org/jira/browse/TRINIDAD-2542
- https://web.archive.org/web/20171129092136/http://www.securitytracker.com/id/1037633
- https://web.archive.org/web/20210123173557/http://www.securityfocus.com/bid/93236
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- http://mail-archives.apache.org/mod_mbox/myfaces-users/201609.mbox/%3CCAM1yOjYM%2BEW3mLUfX0pNAVLfUFRAw-Bhvkp3UE5%3DEQzR8Yxsfw%40mail.gmail.com%3E
- http://packetstormsecurity.com/files/138920/Apache-MyFaces-Trinidad-Information-Disclosure.html
- http://www.oracle.com/technetwork/security-advisory/cpuapr2018-3678067.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2016-2881720.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2017-3236622.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
