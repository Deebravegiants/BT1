# [M] Apache Tomcat Uncontrolled Resource Consumption vulnerability

## Summary
Severity: Medium
Advisory: GHSA-653p-vg55-5652
CVE: CVE-2024-54677
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-12-17
Source: https://github.com/advisories/GHSA-653p-vg55-5652
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=11.0.0-M1 <11.0.2
- Maven: `org.apache.tomcat:tomcat` — affected >=10.1.0-M1 <10.1.34
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.0.M1 <9.0.98

## Details
Uncontrolled Resource Consumption vulnerability in the examples web application provided with Apache Tomcat leads to denial of service.

This issue affects Apache Tomcat: from 11.0.0-M1 through 11.0.1, from 10.1.0-M1 through 10.1.33, from 9.0.0.M1 through 9.9.97. The following versions were EOL at the time the CVE was created but are known to be affected: 8.5.0 though 8.5.100. Other, older, EOL versions may also be affected.

Users are recommended to upgrade to version 11.0.2, 10.1.34 or 9.0.98, which fixes the issue.

This vulnerability does not affect core Apache Tomcat server components (tomcat-catalina, tomcat-coyote, tomcat-embed-core, etc.). Removing the `webapps/examples/` directory in production environments — as recommended by the [Apache Tomcat Security Considerations documentation](https://tomcat.apache.org/tomcat-9.0-doc/security-howto.html#Examples) — eliminates the attack surface entirely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-54677
- https://github.com/apache/tomcat/commit/f57a9d9847c1038be61f5818d73b8be907c460d4
- https://github.com/apache/tomcat/commit/e8c16cdba833884e1bd49fff1f1cb699da177585
- https://github.com/apache/tomcat/commit/dbec927859d9484cb8bd680a7c67b1a560f48444
- https://github.com/apache/tomcat/commit/d63a10afc142b12f462a15f7d10f79fd80ff94eb
- https://github.com/apache/tomcat/commit/cb1707685472994e9d924746f8c91cb116fa5213
- https://github.com/apache/tomcat/commit/c2f7ce21c3fb12caefee87c517a8bb4f80700044
- https://github.com/apache/tomcat/commit/c0a23927ea5e061ca3fdff695138464179fe674a
- https://github.com/apache/tomcat/commit/bbd82e9593314ade4cfd57248f9285fbad686f66
- https://github.com/apache/tomcat/commit/aa5b4d0043289cf054f531ec55126c980d3572e1
- https://github.com/apache/tomcat/commit/a95bf2b0303442a2c9a1ac364b0e63b56049e33a
- https://github.com/apache/tomcat/commit/9ffd23fc27f5d1fc95bf97e5cea175c8968f4533
- https://github.com/apache/tomcat/commit/84c4af76e7a10fc7f8630ce62e6a46632ea4a90e
- https://github.com/apache/tomcat/commit/84065e26ca4555e63a922bb29b13b0a1c86b7654
- https://github.com/apache/tomcat/commit/75ff7e8622edcc024b268677aa789ee8f0880ecc
- https://github.com/apache/tomcat/commit/722814668708c42a61b0c1e340b15bc2b785c0d1
- https://github.com/apache/tomcat/commit/721544ea28e92549824b106be954a9f411867a1c
- https://github.com/apache/tomcat/commit/54e56495e9a106218efe9fc9c79d976c0032bbfd
- https://github.com/apache/tomcat/commit/4f0236606961176257b883213e1621b1859ed746
- https://github.com/apache/tomcat/commit/4d5cc6538d91386f950373ac8120e98c2c78ed3a
