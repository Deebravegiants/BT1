# [H] Restlet is vulnerable to Arbitrary Java Code Execution via crafted XML

## Summary
Severity: High
Advisory: GHSA-92j2-5r7p-6hjw
CVE: CVE-2013-4221
CWE: CWE-91
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-92j2-5r7p-6hjw
Type: github-advisory

## Affected
- Maven: `org.restlet.jse:org.restlet` — affected >=0 <2.1.4

## Details
The default configuration of the ObjectRepresentation class in Restlet before 2.1.4 deserializes objects from untrusted sources using the Java XMLDecoder, which allows remote attackers to execute arbitrary Java code via crafted XML.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4221
- https://github.com/restlet/restlet-framework-java/issues/774
- https://github.com/restlet/restlet-framework-java/commit/b85c2ef182c69c5e2e21df008ccb249ccf80c7b
- https://bugzilla.redhat.com/show_bug.cgi?id=995275
- https://github.com/restlet/restlet-framework-java
- http://blog.diniscruz.com/2013/08/using-xmldecoder-to-execute-server-side.html
- http://restlet.org/learn/2.1/changes
- http://rhn.redhat.com/errata/RHSA-2013-1410.html
- http://rhn.redhat.com/errata/RHSA-2013-1862.html
