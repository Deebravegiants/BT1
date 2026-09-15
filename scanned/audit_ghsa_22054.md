# [M] Jenkins SOASTA CloudTest Plugin stores API token in plain text

## Summary
Severity: Medium
Advisory: GHSA-7hp3-5w4x-8f7c
CVE: CVE-2019-10451
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7hp3-5w4x-8f7c
Type: github-advisory

## Affected
- Maven: `com.soasta.jenkins:cloudtest` — affected >=0

## Details
Jenkins SOASTA CloudTest Plugin stores credentials unencrypted in its global configuration file `com.soasta.jenkins.CloudTestServer.xml` on the Jenkins controller. These credentials could be viewed by users with access to the Jenkins controller file system.

As of publication of this advisory there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10451
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1439
