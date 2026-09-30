# [C] Deserialization of Untrusted Data in Apache commons collections

## Summary
Severity: Critical
Advisory: GHSA-fjq5-5j5f-mvxh
CVE: CVE-2015-7501
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-fjq5-5j5f-mvxh
Type: github-advisory

## Affected
- Maven: `commons-collections:commons-collections` — affected >=0 <3.2.2
- Maven: `org.apache.commons:commons-collections4` — affected >=0 <4.1
- Maven: `org.apache.servicemix.bundles:org.apache.servicemix.bundles.commons-collections` — affected >=3.2.1
- Maven: `net.sourceforge.collections:collections-generic` — affected 4.01
- Maven: `org.apache.servicemix.bundles:org.apache.servicemix.bundles.collections-generic` — affected >=4.01

## Details
It was found that the Apache commons-collections library permitted code execution when deserializing objects involving a specially constructed chain of classes. A remote attacker could use this flaw to execute arbitrary code with the permissions of the application using the commons-collections library.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7501
- https://access.redhat.com/security/vulnerabilities/2059393
- https://access.redhat.com/solutions/2045023
- https://arxiv.org/pdf/2306.05534.pdf
- https://bugzilla.redhat.com/show_bug.cgi?id=1279330
- https://commons.apache.org/proper/commons-collections/release_4_1.html
- https://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability
- https://github.com/apache/commons-collections
- https://github.com/jensdietrich/xshady-release/tree/main/CVE-2015-7501
- https://issues.apache.org/jira/browse/COLLECTIONS-580.
- https://sourceforge.net/p/collections/code/HEAD/tree
- http://rhn.redhat.com/errata/RHSA-2016-1773.html
