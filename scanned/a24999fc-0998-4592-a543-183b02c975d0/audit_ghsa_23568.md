# [H] ClassLoader manipulation in Apache Struts

## Summary
Severity: High
Advisory: GHSA-prjv-jj26-wf8h
CVE: CVE-2014-0112
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-prjv-jj26-wf8h
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=0 <2.3.20

## Details
ParametersInterceptor in Apache Struts before 2.3.20 does not properly restrict access to the getClass method, which allows remote attackers to "manipulate" the ClassLoader and execute arbitrary code via a crafted request. NOTE: this vulnerability exists because of an incomplete fix for CVE-2014-0094.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0112
- https://access.redhat.com/errata/RHSA-2019:0910
- https://bugzilla.redhat.com/show_bug.cgi?id=1091939
- https://cwiki.apache.org/confluence/display/WW/S2-021
- https://github.com/apache/struts
- http://jvn.jp/en/jp/JVN19294237/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2014-000045
- http://packetstormsecurity.com/files/127215/VMware-Security-Advisory-2014-0007.html
- http://www-01.ibm.com/support/docview.wss?uid=swg21676706
- http://www.oracle.com/technetwork/topics/security/cpuapr2015-2365600.html
- http://www.vmware.com/security/advisories/VMSA-2014-0007.html
