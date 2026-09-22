# [M] Improper Neutralization of Input During Web Page Generation in Mojarra

## Summary
Severity: Medium
Advisory: GHSA-3m3r-82gc-53mj
CVE: CVE-2013-5855
CWE: CWE-79
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-3m3r-82gc-53mj
Type: github-advisory

## Affected
- Maven: `org.glassfish:javax.faces` — affected >=2.2.0 <2.2.6
- Maven: `org.glassfish:javax.faces` — affected >=2.1.0 <2.1.28

## Details
Oracle Mojarra 2.2.x before 2.2.6 and 2.1.x before 2.1.28 does not perform appropriate encoding when a (1) <h:outputText> tag or (2) EL expression is used after a scriptor style block, which allows remote attackers to conduct cross-site scripting (XSS) attacks via application-specific vectors.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-5855
- https://java.net/jira/browse/JAVASERVERFACES-3150
- https://java.net/jira/browse/JAVASERVERFACES_SPEC_PUBLIC-1258
- http://h30499.www3.hp.com/t5/HP-Security-Research-Blog/JSF-outputText-tag-the-good-the-bad-and-the-ugly/ba-p/6368011#.U8ccVPlXZHU
- http://rhn.redhat.com/errata/RHSA-2015-0675.html
- http://rhn.redhat.com/errata/RHSA-2015-0720.html
- http://rhn.redhat.com/errata/RHSA-2015-0765.html
- http://seclists.org/fulldisclosure/2014/Dec/23
- http://www.oracle.com/technetwork/topics/security/cpujan2016-2367955.html
- http://www.oracle.com/technetwork/topics/security/cpujul2014-1972956.html
- http://www.vmware.com/security/advisories/VMSA-2014-0012.html
