# [C] Apache Tomcat affected by vulnerability in TLS and SSL protocol

## Summary
Severity: Critical
Advisory: GHSA-f7w7-6pjc-wwm6
CVE: CVE-2009-3555
CWE: CWE-295, CWE-300
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-f7w7-6pjc-wwm6
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.10
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.32
- Maven: `org.apache.tomcat:tomcat` — affected >=5.0.0 <5.5.33

## Details
The TLS protocol, and the SSL protocol 3.0 and possibly earlier, as used in Microsoft Internet Information Services (IIS) 7.0, mod_ssl in the Apache HTTP Server 2.2.14 and earlier, OpenSSL before 0.9.8l, GnuTLS 2.8.5 and earlier, Mozilla Network Security Services (NSS) 3.12.4 and earlier, multiple Cisco products, and other products, does not properly associate renegotiation handshakes with an existing connection, which allows man-in-the-middle attackers to insert data into HTTPS sessions, and possibly other types of sessions protected by TLS or SSL, by sending an unauthenticated request that is processed retroactively by a server in a post-renegotiation context, related to a "plaintext injection" attack, aka the "Project Mogul" issue.

Apache Tomcat was affected by this issue and introduced a workaround in versions 7.0.10, 6.0.32, and 5.5.33.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-3555
- https://github.com/apache/tomcat/commit/df9633116b5fec8f47f1f008fb89a6e9d5895cd0
- https://github.com/apache/tomcat/commit/b4e9488629bf03b4b65abf335e536e85386d1366
- https://github.com/apache/tomcat/commit/56f67141e82e16f68a860c3af9b7342da35cbe7d
- https://github.com/apache/tomcat/commit/3d315ac9dfaa2c03b4df82938d78bf5b755766b3
- https://github.com/apache/tomcat/commit/328a523cbb2a2d4cd55283180614d4e03e2f8f02
- https://github.com/apache/tomcat/commit/30af3f5630542a2340781f66553e734a6fd69701
- https://github.com/apache/tomcat/commit/2d4ca03acc27cc883c404d1745d92f983b6fada3
- https://github.com/apache/tomcat/commit/14e4efd925da58b9fa63f20969fb7349b8a9c30d
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A8535
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A8366
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A7973
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A7478
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A7315
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A11617
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A11578
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A10088
- https://lists.apache.org/thread.html/rf8e8c091182b45daa50d3557cad9b10bb4198e3f08cf8f1c66a1b08d%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/re3b72cbb13e1dfe85c4a06959a3b6ca6d939b407ecca80db12b54220%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/f8e0814e11c7f21f42224b6de111cb3f5e5ab5c15b78924c516d4ec2%40%3Cdev.tomcat.apache.org%3E
