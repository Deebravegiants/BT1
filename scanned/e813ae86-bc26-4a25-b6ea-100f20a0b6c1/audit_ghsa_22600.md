# [H] Jenkins Maven Release Plug-in Plugin XXE vulnerability

## Summary
Severity: High
Advisory: GHSA-7mf5-79gv-66gh
CVE: CVE-2019-16549
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7mf5-79gv-66gh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.m2release:m2release` — affected >=0 <0.16.2

## Details
Jenkins Maven Release Plug-in Plugin retrieves XML from Nexus repository manager APIs. Maven Release Plug-in Plugin 0.16.1 and earlier does not configure the XML parser to prevent XML external entity (XXE) attacks. While Jenkins users without Overall/Administer permission are not allowed to configure a custom Nexus URL, this could still be exploited via man-in-the-middle attacks, especially if it’s not an HTTPS URL.

Additionally, a connection test form validation method does not require POST requests, resulting in a cross-site request forgery vulnerability. Combined, these two vulnerabilities allow attackers to have Jenkins parse crafted XML documents that use external entities for extraction of secrets from the Jenkins controller, server-side request forgery, or denial-of-service attacks.

Maven Release Plug-in Plugin 0.16.2 configures its XML parser to prevent XML external entity (XXE) attacks. It also now requires that requests to the connection test form validation method are done via POST, which protects from cross-site request forgery attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16549
- https://github.com/jenkinsci/m2release-plugin/commit/1e4d6fee2eab16e7a396b6d3d5f10a87e5c29cc2
- https://jenkins.io/security/advisory/2019-12-17/#SECURITY-1681
- http://www.openwall.com/lists/oss-security/2019/12/17/1
