# [C] Deserialization of Untrusted Data in Groovy

## Summary
Severity: Critical
Advisory: GHSA-xphj-m9cc-8fmq
CVE: CVE-2016-6814
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-xphj-m9cc-8fmq
Type: github-advisory

## Affected
- Maven: `org.codehaus.groovy:groovy` — affected >=1.7.0 <2.4.8
- Maven: `org.codehaus.groovy:groovy-all` — affected >=1.7.0 <2.4.8

## Details
When an application with unsupported Codehaus versions of Groovy from 1.7.0 to 2.4.3, Apache Groovy 2.4.4 to 2.4.7 on classpath uses standard Java serialization mechanisms, e.g. to communicate between servers or to store local data, it was possible for an attacker to bake a special serialized object that will execute code directly when deserialized. All applications which rely on serialization and do not isolate the code which deserializes objects were subject to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6814
- https://access.redhat.com/errata/RHSA-2017:0868
- https://access.redhat.com/errata/RHSA-2017:2486
- https://access.redhat.com/errata/RHSA-2017:2596
- https://security.gentoo.org/glsa/202003-01
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- http://mail-archives.apache.org/mod_mbox/www-announce/201701.mbox/%3CCADRx3PMZ2hBCGDTY35zYXFGaDnjAs0tc5-upaVs6QN2sYUejyA%40mail.gmail.com%3E
- http://rhn.redhat.com/errata/RHSA-2017-0272.html
- http://www.oracle.com/technetwork/security-advisory/cpuapr2018-3678067.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
