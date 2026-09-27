# [M] API keys stored in plain text by Jenkins Katalon Plugin

## Summary
Severity: Medium
Advisory: GHSA-35rx-7pc8-6963
CVE: CVE-2022-43419
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-35rx-7pc8-6963
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:katalon` — affected >=0 <1.0.33

## Details
Jenkins Katalon Plugin 1.0.32 and earlier stores API keys unencrypted in job `config.xml` files on the Jenkins controller as part of its configuration.

These API keys can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

Katalon Plugin 1.0.33 no longer stores the API keys directly, instead accessing them through its [Credentials Plugin](https://plugins.jenkins.io/credentials) integration, once affected job configurations are saved again.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43419
- https://github.com/jenkinsci/katalon-plugin/pull/28
- https://github.com/jenkinsci/katalon-plugin/commit/64f819387f3f14d54f3a1542578a5c7aa9feb85c
- https://github.com/jenkinsci/katalon-plugin
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2846
- http://www.openwall.com/lists/oss-security/2022/10/19/3
