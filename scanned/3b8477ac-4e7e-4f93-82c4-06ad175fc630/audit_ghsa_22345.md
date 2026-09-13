# [C] Arbitrary code execution in Apache Struts 2

## Summary
Severity: Critical
Advisory: GHSA-4prj-vw9j-v6pr
CVE: CVE-2016-4438
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-4prj-vw9j-v6pr
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=2.3.19 <2.3.29
- Maven: `org.apache.struts:struts2-rest-plugin` — affected >=2.3.19 <2.3.29

## Details
The REST plugin in Apache Struts 2 2.3.19 through 2.3.28.1 allows remote attackers to execute arbitrary code via a crafted expression.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4438
- https://github.com/apache/struts/commit/6d7ac40dcede1793a4534a3dc249fd562d495e8c
- https://github.com/apache/struts/commit/76eb8f38a33ad0f1f48464ee1311559c8d52dd6d
- https://github.com/apache/struts/commit/c9c21378f2fb2ff21355c128c45e106ebd87ad7c
- https://github.com/apache/struts/commit/deefeffd11425f0cd0b797cd86a9b3550234262b
- https://bugzilla.redhat.com/show_bug.cgi?id=1348238
- https://github.com/apache/struts
- https://struts.apache.org/docs/s2-037.html
- http://jvn.jp/en/jp/JVN07710476/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2016-000110
