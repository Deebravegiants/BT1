# [H] Restlet Arbitrary Java Code Execution via a serialized object

## Summary
Severity: High
Advisory: GHSA-f3mv-g3xr-fp7w
CVE: CVE-2013-4271
CWE: CWE-502
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-f3mv-g3xr-fp7w
Type: github-advisory

## Affected
- Maven: `org.restlet.jse:org.restlet` — affected >=0 <2.1.4

## Details
The default configuration of the ObjectRepresentation class in Restlet before 2.1.4 deserializes objects from untrusted sources, which allows remote attackers to execute arbitrary Java code via a serialized object, a different vulnerability than CVE-2013-4221.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4271
- https://github.com/restlet/restlet-framework-java/issues/778
- https://bugzilla.redhat.com/show_bug.cgi?id=999735
- https://github.com/restlet/restlet-framework-java
- http://restlet.org/learn/2.1/changes
- http://rhn.redhat.com/errata/RHSA-2013-1410.html
- http://rhn.redhat.com/errata/RHSA-2013-1862.html
