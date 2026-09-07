# [C] Improper Neutralization of Special Elements in Output Used by a Downstream Component in Apache Groovy

## Summary
Severity: Critical
Advisory: GHSA-qg25-hgjv-cg9q
CVE: CVE-2015-3253
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-qg25-hgjv-cg9q
Type: github-advisory

## Affected
- Maven: `org.codehaus.groovy:groovy` — affected >=1.7.0 <2.4.4
- Maven: `org.codehaus.groovy:groovy-all` — affected >=1.7.0 <2.4.4

## Details
The MethodClosure class in runtime/MethodClosure.java in Apache Groovy 1.7.0 through 2.4.3 allows remote attackers to execute arbitrary code or cause a denial of service via a crafted serialized object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3253
- https://access.redhat.com/errata/RHSA-2016:1376
- https://access.redhat.com/errata/RHSA-2017:2486
- https://access.redhat.com/errata/RHSA-2017:2596
- https://github.com/apache/groovy
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05324755
- https://lists.apache.org/thread.html/rbb8e16cc5acab183124572b655bdf5fe1d5b5f477dc267352426c7ed@%3Cnotifications.shardingsphere.apache.org%3E
- https://security.gentoo.org/glsa/201610-01
- https://security.netapp.com/advisory/ntap-20160623-0001
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- http://groovy-lang.org/security.html
- http://packetstormsecurity.com/files/132714/Apache-Groovy-2.4.3-Code-Execution.html
- http://rhn.redhat.com/errata/RHSA-2016-0066.html
- http://www.oracle.com/technetwork/security-advisory/cpuapr2016v3-2985753.html
- http://www.oracle.com/technetwork/security-advisory/cpujan2018-3236628.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2016-2881720.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2017-3236622.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2016-2881722.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
