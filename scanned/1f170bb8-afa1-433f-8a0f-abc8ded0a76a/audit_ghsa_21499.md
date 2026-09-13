# [H] Apache Tomcat may reject request containing invalid Content-Length header

## Summary
Severity: High
Advisory: GHSA-p22x-g9px-3945
CVE: CVE-2022-42252
CWE: CWE-20, CWE-444
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-11-01
Source: https://github.com/advisories/GHSA-p22x-g9px-3945
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.0 <8.5.83
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0-M1 <9.0.68
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.0.0-M1 <10.0.27
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.0-M1 <10.1.1
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=9.0.0-M1 <9.0.68
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=10.0.0-M1 <10.0.27
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=10.1.0-M1 <10.1.1

## Details
If Apache Tomcat 8.5.0 to 8.5.82, 9.0.0-M1 to 9.0.67, 10.0.0-M1 to 10.0.26 or 10.1.0-M1 to 10.1.0 was configured to ignore invalid HTTP headers via setting rejectIllegalHeader to false (the default for 8.5.x only), Tomcat did not reject a request containing an invalid Content-Length header making a request smuggling attack possible if Tomcat was located behind a reverse proxy that also failed to reject the request with the invalid header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42252
- https://github.com/apache/tomcat/commit/0d089a15047faf9cb3c82f80f4d28febd4798920
- https://github.com/apache/tomcat/commit/4c7f4fd09d2cc1692112ef70b8ee23a7a037ae77
- https://github.com/apache/tomcat/commit/a1c07906d8dcaf7957e5cc97f5cdbac7d18a205a
- https://github.com/apache/tomcat/commit/c9fe754e5d17e262dfbd3eab2a03ca96ff372dc3
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/zzcxzvqfdqn515zfs3dxb7n8gty589sq
- https://security.gentoo.org/glsa/202305-37
- https://tomcat.apache.org/security-10.html
- https://tomcat.apache.org/security-8.html
- https://tomcat.apache.org/security-9.html
