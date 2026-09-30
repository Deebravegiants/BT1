# [M] Exposure of Sensitive Information in Gradle publish plugin

## Summary
Severity: Medium
Advisory: GHSA-cv78-v957-jx34
CVE: CVE-2020-7599
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cv78-v957-jx34
Type: github-advisory

## Affected
- Maven: `com.gradle.publish:plugin-publish-plugin` — affected >=0 <0.11.0
- Maven: `com.gradle.plugin-publish:com.gradle.plugin-publish.gradle.plugin` — affected >=0 <0.11.0

## Details
All versions of com.gradle.plugin-publish before 0.11.0 are vulnerable to Insertion of Sensitive Information into Log File. When a plugin author publishes a Gradle plugin while running Gradle with the --info log level flag, the Gradle Logger logs an AWS pre-signed URL. If this build log is publicly visible (as it is in many popular public CI systems like TravisCI) this AWS pre-signed URL would allow a malicious actor to replace a recently uploaded plugin with their own.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7599
- https://blog.gradle.org/plugin-portal-update
- https://plugins.gradle.org/plugin/com.gradle.plugin-publish
- https://snyk.io/vuln/SNYK-JAVA-COMGRADLEPLUGINPUBLISH-559866
