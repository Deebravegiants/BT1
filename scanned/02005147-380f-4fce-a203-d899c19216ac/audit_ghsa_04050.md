# [H] Information exposure in FasterXML jackson-databind

## Summary
Severity: High
Advisory: GHSA-5ww9-j83m-q7qx
CVE: CVE-2019-12086
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-05-23
Source: https://github.com/advisories/GHSA-5ww9-j83m-q7qx
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.9.0 <2.9.9
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.8.0 <2.8.11.4
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.7.0 <2.7.9.6
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.0.0 <2.6.7.3

## Details
A Polymorphic Typing issue was discovered in FasterXML jackson-databind 2.x before 2.9.9. When Default Typing is enabled (either globally or for a specific property) for an externally exposed JSON endpoint, the service has the mysql-connector-java jar (8.0.14 or earlier) in the classpath, and an attacker can host a crafted MySQL server reachable by the victim, an attacker can send a crafted JSON message that allows them to read arbitrary local files on the server. This occurs because of missing com.mysql.cj.jdbc.admin.MiniAdmin validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12086
- https://github.com/FasterXML/jackson-databind/issues/2326
- https://github.com/FasterXML/jackson-databind/commit/efc3c0d02f4743dbaa6d1b9c466772a2f13d966b
- https://github.com/FasterXML/jackson-databind/commit/dda513bd7251b4f32b7b60b1c13740e3b5a43024
- https://github.com/FasterXML/jackson-databind/commit/d30f036208ab1c60bd5ce429cb4f7f1a3e5682e8
- https://lists.apache.org/thread.html/rca37935d661f4689cb4119f1b3b224413b22be161b678e6e6ce0c69b@%3Ccommits.nifi.apache.org%3E
- https://lists.apache.org/thread.html/rda99599896c3667f2cc9e9d34c7b6ef5d2bbed1f4801e1d75a2b0679@%3Ccommits.nifi.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2019/05/msg00030.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OVRZDN2T6AZ6DJCZJ3VSIQIVHBVMVWBL
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TXRVXNRFHJSQWFHPRJQRI5UPMZ63B544
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UKUALE2TUCKEKOHE2D342PQXN4MWCSLC
- https://medium.com/@cowtowncoder/on-jackson-cves-dont-panic-here-is-what-you-need-to-know-54cd0d6e8062
- https://seclists.org/bugtraq/2019/May/68
- https://security.netapp.com/advisory/ntap-20190530-0003
- https://web.archive.org/web/20200227030031/http://www.securityfocus.com/bid/109227
- https://web.archive.org/web/20200808181049/http://russiansecurity.expert/2016/04/20/mysql-connect-file-read
- https://www.debian.org/security/2019/dsa-4452
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
