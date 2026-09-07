# [H] Unrestricted Upload of File with Dangerous Type Apache Tomcat

## Summary
Severity: High
Advisory: GHSA-xjgh-84hx-56c5
CVE: CVE-2017-12617
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-xjgh-84hx-56c5
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=9.0.0.M1 <9.0.1
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=8.5.0 <8.5.23
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=8.0.0-RC1 <8.0.47
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=7.0.0 <7.0.82
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0.M1 <9.0.1
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.0 <8.5.23
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.0.0-RC1 <8.0.47
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=7.0.0 <7.0.82

## Details
When running Apache Tomcat versions 9.0.0.M1 to 9.0.0, 8.5.0 to 8.5.22, 8.0.0.RC1 to 8.0.46 and 7.0.0 to 7.0.81 with HTTP PUTs enabled (e.g. via setting the readonly initialisation parameter of the Default servlet to false) it was possible to upload a JSP file to the server via a specially crafted request. This JSP could then be requested and any code it contained would be executed by the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12617
- https://github.com/apache/tomcat/commit/a9dd96046d7acb0357c6b7b9e6cc70d186fae663
- https://github.com/apache/tomcat/commit/74ad0e216c791454a318c1811300469eedc5c6f3
- https://github.com/apache/tomcat/commit/512a3c3aecdb52de092c6bacddd71b85c4feda06
- https://github.com/apache/tomcat/commit/506d862e7edfa991de198e0f2e4c4540830fa531
- https://github.com/apache/tomcat/commit/4cf7dab88282c8f3c92f0b961cdb0096e1d63e88
- https://github.com/apache/tomcat/commit/46dfedbc0523d7182be97f4244d7b6c942164485
- https://github.com/apache/tomcat/commit/327e8a6644e188764325a013aa2725a60f1b37e5
- https://github.com/apache/tomcat/commit/31e99502e2c602449a2f8835bd23ade772b77333
- https://github.com/apache/tomcat/commit/24aea94807f940ee44aa550378dc903289039ddd
- https://github.com/apache/tomcat/commit/b577f9a7996b92b650b1649af3c3bae11c120db9
- https://github.com/apache/tomcat/commit/b7e0435d17aba69f16ae9e8a78ad0f1565b552af
- https://github.com/apache/tomcat/commit/bbcbb749c75056a2781f37038d63e646fe972104
- https://github.com/apache/tomcat/commit/c177e9668d1278710bdb14c0eb8d2702b3655f5a
- https://github.com/apache/tomcat/commit/cf0b37beb0622abdf24acc7110daf883f3fe4f95
- https://github.com/apache/tomcat/commit/d5b170705d24c386d76038e5989045c89795c28c
- https://github.com/apache/tomcat/commit/e650cf1b83e441dbd3863f3f6b61c972cafce19e
- https://github.com/apache/tomcat/commit/f1b85da754c4760787d68a99e839b50878140b57
- https://github.com/apache/tomcat/commit/fd52f8601170b91f9d7162510e54563e5bf6bdfe
- https://lists.apache.org/thread.html/r6ccee4e849bc77df0840c7f853f6bd09d426f6741247da2b7429d5d9@%3Cdev.tomcat.apache.org%3E
