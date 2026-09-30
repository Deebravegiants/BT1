# [M] Missing XML Validation in Apache Tomcat

## Summary
Severity: Medium
Advisory: GHSA-prc3-7f44-w48j
CVE: CVE-2014-0119
CWE: CWE-112
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-prc3-7f44-w48j
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=0 <6.0.40
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.54
- Maven: `org.apache.tomcat:tomcat` — affected >=8.0.0 <8.0.6
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=0 <6.0.40
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=7.0.0 <7.0.54
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=8.0.0 <8.0.6
- Maven: `org.apache.tomcat:tomcat-jasper` — affected >=0 <6.0.40
- Maven: `org.apache.tomcat:tomcat-jasper` — affected >=7.0.0 <7.0.54
- Maven: `org.apache.tomcat:tomcat-jasper` — affected >=8.0.0 <8.0.6

## Details
Apache Tomcat before 6.0.40, 7.x before 7.0.54, and 8.x before 8.0.6 does not properly constrain the class loader that accesses the XML parser used with an XSLT stylesheet, which allows remote attackers to (1) read arbitrary files via a crafted web application that provides an XML external entity declaration in conjunction with an entity reference, related to an XML External Entity (XXE) issue, or (2) read files associated with different web applications on a single Tomcat instance via a crafted web application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0119
- https://github.com/apache/tomcat80/commit/d59fd4398c8ae6361e0b13c491f66b51e49a7441
- https://github.com/apache/tomcat80/commit/7d33457de5fc5a652a88fb9bbc9ba4cbbda58f04
- https://github.com/apache/tomcat80/commit/77e014cef5d5af619bcf77eaebf22c284d420802
- https://github.com/apache/tomcat80/commit/69a8a72283c3395ece8b899cf8562e126de97a27
- https://github.com/apache/tomcat80/commit/51e59532ad4c604f55575963dc7a7f0250cb420f
- https://github.com/apache/tomcat80/commit/4d90e355dc5ced4c53585c2b4700f71a52d8f447
- https://github.com/apache/tomcat80/commit/25251de791a6a7be13f2f3d3a66119a77025272d
- https://github.com/apache/tomcat/commit/f8b316acbbf9fabf87cc137e9777e912eda0d834
- https://github.com/apache/tomcat/commit/ebe5c16f18ce1559e8462a94b3876a98525980d2
- https://github.com/apache/tomcat/commit/080878ea519d8c74c53721a9ebf7be6fcf6f1f2f
- https://github.com/apache/tomcat/commit/50311bed8d87e452ff0e69838ba312c4fe899b2d
- https://github.com/apache/tomcat/commit/5517c5517e8a7ddb994504f0c5c05001a376b10c
- https://github.com/apache/tomcat/commit/5aae1323c31d643afa9f2db80713b8e97b5123af
- https://github.com/apache/tomcat/commit/6246d8307fb5f2b4ff0b0f4d6d1b0250dff01a81
- https://github.com/apache/tomcat/commit/769477b9bc8442db3f571385fa0c3e206242cbf1
- https://github.com/apache/tomcat/commit/934f884f330dad192d2c5dc950e28f4cd281461b
- https://github.com/apache/tomcat/commit/ad3b34a290a0255d2a4c356a3611ab41ed9d04f5
- https://github.com/apache/tomcat/commit/ce70ee6b8fe437a498a375215011056702b0c481
- https://github.com/apache/tomcat
