# [H] Restlet Framework allows remote attackers to access arbitrary files via a crafted REST API HTTP request

## Summary
Severity: High
Advisory: GHSA-cvj4-g3gx-8vqq
CVE: CVE-2017-14949
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-cvj4-g3gx-8vqq
Type: github-advisory

## Affected
- Maven: `org.restlet.jse:org.restlet` — affected >=0 <2.3.12

## Details
Restlet Framework before 2.3.12 allows remote attackers to access arbitrary files via a crafted REST API HTTP request that conducts an XXE attack, because only general external entities (not parameter external entities) are properly considered. This is related to XmlRepresentation, DOMRepresentation, SaxRepresentation, and JacksonRepresentation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14949
- https://github.com/restlet/restlet-framework-java/commit/fe75aff3af23b879b984db7a2b6824cee0ef0fc5
- https://github.com/advisories/GHSA-cvj4-g3gx-8vqq
- https://github.com/restlet/restlet-framework-java
- https://github.com/restlet/restlet-framework-java/wiki/XEE-security-enhancements
- https://lgtm.com/blog/restlet_CVE-2017-14949
