# [H] Code injection in Apache Struts

## Summary
Severity: High
Advisory: GHSA-j7h6-xr7g-m2c5
CVE: CVE-2013-4316
CWE: CWE-94
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j7h6-xr7g-m2c5
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=2.0.0 <2.3.15.2
- Maven: `org.apache.struts:struts2-rest-plugin` — affected >=2.0.0 <2.3.15.2

## Details
Apache Struts 2.0.0 through 2.3.15.1 enables Dynamic Method Invocation by default, which has unknown impact and attack vectors.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4316
- https://github.com/apache/struts/commit/58947c3f85ae641c1a476316a2888e53605948d1
- https://github.com/apache/struts/commit/c643336945dda84cbcdc8a39530baa24fede28c4
- https://github.com/apache/struts
- http://archives.neohapsis.com/archives/bugtraq/2013-09/0107.html
- http://struts.apache.org/release/2.3.x/docs/s2-019.html
