# [H] Restlet Framework Ja-rs extension is vulnerable to XXE when using SimpleXMLProvider

## Summary
Severity: High
Advisory: GHSA-2mp8-qvqm-3xwq
CVE: CVE-2017-14868
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-2mp8-qvqm-3xwq
Type: github-advisory

## Affected
- Maven: `org.restlet.jse:org.restlet.ext.jaxrs` — affected >=0 <2.3.11

## Details
Restlet Framework before 2.3.11, when using SimpleXMLProvider, allows remote attackers to access arbitrary files via an XXE attack in a REST API HTTP request. This affects use of the Jax-rs extension.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14868
- https://github.com/restlet/restlet-framework-java/issues/1286
- https://github.com/advisories/GHSA-2mp8-qvqm-3xwq
- https://github.com/restlet/restlet-framework-java
- https://github.com/restlet/restlet-framework-java/wiki/XEE-security-enhancements
- https://lgtm.com/blog/restlet_CVE-2017-14868
