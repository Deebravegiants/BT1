# [H] OrientDB-Server vulnerable to Cross-Site Request Forgery

## Summary
Severity: High
Advisory: GHSA-p8ww-vv84-c2rm
CVE: CVE-2015-2912
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-p8ww-vv84-c2rm
Type: github-advisory

## Affected
- Maven: `com.orientechnologies:orientdb-studio` — affected >=0 <2.0.15
- Maven: `com.orientechnologies:orientdb-studio` — affected >=2.1.0 <2.1.1

## Details
The JSONP endpoint in the Studio component in OrientDB Server Community Edition before 2.0.15 and 2.1.x before 2.1.1 does not properly restrict callback values, which allows remote attackers to conduct cross-site request forgery (CSRF) attacks, and obtain sensitive information, via a crafted HTTP request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-2912
- https://github.com/orientechnologies/orientdb/issues/4824
- https://github.com/advisories/GHSA-p8ww-vv84-c2rm
- https://github.com/orientechnologies/orientdb
- https://www.kb.cert.org/vuls/id/845332
