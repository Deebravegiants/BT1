# [M] Moderate severity vulnerability that affects org.restlet.jse:org.restlet

## Summary
Severity: Medium
Advisory: GHSA-73cq-fhp3-8rpw
CVE: CVE-2014-1868
CWE: CWE-776
Ecosystem: Maven
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-73cq-fhp3-8rpw
Type: github-advisory

## Affected
- Maven: `org.restlet.jse:org.restlet` — affected >=2.1.0 <2.1.7

## Details
Restlet Framework 2.1.x before 2.1.7 and 2.x.x before 2.2 RC1, when using XMLRepresentation or XML serializers, allows attackers to cause a denial of service via an XML Entity Expansion (XEE) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-1868
- https://exchange.xforce.ibmcloud.com/vulnerabilities/91181
- https://github.com/advisories/GHSA-73cq-fhp3-8rpw
- https://github.com/restlet/restlet-framework-java
- https://github.com/restlet/restlet-framework-java/wiki/XEE-security-enhancements
- http://secunia.com/advisories/56940
