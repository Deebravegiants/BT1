# [H] Neo4J vulnerable to Cross-Site Request Forgery

## Summary
Severity: High
Advisory: GHSA-x626-q4v7-7xc6
CVE: CVE-2013-7259
CWE: CWE-352, CWE-78
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-x626-q4v7-7xc6
Type: github-advisory

## Affected
- Maven: `org.neo4j:neo4j` — affected >=0 <2.2.0-M01

## Details
Multiple cross-site request forgery (CSRF) vulnerabilities in Neo4J 1.9.2 allow remote attackers to hijack the authentication of administrators for requests that execute arbitrary code, as demonstrated by a request to (1) db/data/ext/GremlinPlugin/graphdb/execute_script or (2) db/manage/server/console/.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7259
- https://github.com/neo4j/neo4j/issues/2826
- https://github.com/neo4j/neo4j/commit/40ad76078a25666d8b218772b6491fb443020df9
- https://github.com/neo4j/neo4j
- https://github.com/o2platform/DefCon_RESTing/tree/master/Live-Demos/Neo4j
- https://web.archive.org/web/20131017043717/http://blog.diniscruz.com/2013/08/neo4j-csrf-payload-to-start-processes.html
- http://www.openwall.com/lists/oss-security/2014/01/03/3
- http://www.openwall.com/lists/oss-security/2014/01/03/8
