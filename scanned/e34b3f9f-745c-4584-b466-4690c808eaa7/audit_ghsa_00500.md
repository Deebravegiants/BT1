# [H] Files or Directories Accessible to External Parties in org.springframework:spring-core

## Summary
Severity: High
Advisory: GHSA-pgf9-h69p-pcgf
CVE: CVE-2015-5211
CWE: CWE-20, CWE-552
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-pgf9-h69p-pcgf
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-core` — affected >=4.2.0 <4.2.2
- Maven: `org.springframework:spring-core` — affected >=4.0.0 <4.1.8
- Maven: `org.springframework:spring-core` — affected >=0 <3.2.15

## Details
Under some situations, the Spring Framework 4.2.0 to 4.2.1, 4.0.0 to 4.1.7, 3.2.0 to 3.2.14 and older unsupported versions is vulnerable to a Reflected File Download (RFD) attack. The attack involves a malicious user crafting a URL with a batch script extension that results in the response being downloaded rather than rendered and also includes some input reflected in the response.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5211
- https://github.com/spring-projects/spring-framework/commit/03f547eb9868f48f44d59b56067d4ac4740672c3
- https://github.com/spring-projects/spring-framework/commit/2bd1daa75ee0b8ec33608ca6ab065ef3e1815543
- https://github.com/spring-projects/spring-framework/commit/a95c3d820dbc4c3ae752f1b3ee22ee860b162402
- https://github.com/advisories/GHSA-pgf9-h69p-pcgf
- https://github.com/spring-projects/spring-framework
- https://lists.debian.org/debian-lts-announce/2019/07/msg00012.html
- https://pivotal.io/security/cve-2015-5211
- https://www.trustwave.com/Resources/SpiderLabs-Blog/Reflected-File-Download---A-New-Web-Attack-Vector
