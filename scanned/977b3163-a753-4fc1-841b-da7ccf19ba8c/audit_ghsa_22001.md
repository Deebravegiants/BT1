# [M] Stored XSS vulnerability in Jenkins Generic Webhook Trigger Plugin

## Summary
Severity: Medium
Advisory: GHSA-qqwx-hcp6-25vr
CVE: CVE-2022-25185
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-qqwx-hcp6-25vr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:generic-webhook-trigger` — affected >=0 <1.82

## Details
Jenkins Generic Webhook Trigger Plugin 1.81 and earlier does not escape the build cause when using the webhook, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25185
- https://github.com/jenkinsci/generic-webhook-trigger-plugin/commit/b289c32aa74439f3a8deb7674128a3a6fd90a61c
- https://github.com/jenkinsci/generic-webhook-trigger-plugin
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2592
- http://www.openwall.com/lists/oss-security/2022/02/15/2
