# [M] Improper Authentication in Apache MyFaces

## Summary
Severity: Medium
Advisory: GHSA-4fv4-cq5v-x45m
CVE: CVE-2010-2057
CWE: CWE-287
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4fv4-cq5v-x45m
Type: github-advisory

## Affected
- Maven: `org.apache.myfaces.shared:myfaces-shared-core` — affected >=1.1.0 <1.1.8
- Maven: `org.apache.myfaces.shared:myfaces-shared-core` — affected >=1.2.0 <1.2.9
- Maven: `org.apache.myfaces.shared:myfaces-shared-core` — affected >=2.0.0 <2.0.1
- Maven: `org.apache.myfaces.core:myfaces-impl` — affected >=1.1.0 <1.1.8
- Maven: `org.apache.myfaces.core:myfaces-impl` — affected >=1.2.0 <1.2.9
- Maven: `org.apache.myfaces.core:myfaces-impl` — affected >=2.0.0 <2.0.1

## Details
shared/util/StateUtils.java in Apache MyFaces 1.1.x before 1.1.8, 1.2.x before 1.2.9, and 2.0.x before 2.0.1 uses an encrypted View State without a Message Authentication Code (MAC), which makes it easier for remote attackers to perform successful modifications of the View State via a padding oracle attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-2057
- https://bugzilla.redhat.com/show_bug.cgi?id=623799
- https://issues.apache.org/jira/browse/MYFACES-2749
- http://svn.apache.org/viewvc/myfaces/shared/trunk/core/src/main/java/org/apache/myfaces/shared/util/StateUtils.java?r1=943327&r2=951801
