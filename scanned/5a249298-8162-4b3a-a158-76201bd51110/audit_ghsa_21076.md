# [M] Jenkins OpsGenie Plugin Plaintext Storage of a Password vulnerability

## Summary
Severity: Medium
Advisory: GHSA-273c-fjw8-v2w8
CVE: CVE-2022-34803
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-273c-fjw8-v2w8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:opsgenie` — affected >=0

## Details
Jenkins OpsGenie Plugin 1.9 and earlier stores API keys unencrypted in its global configuration file `com.opsgenie.integration.jenkins.OpsGenieNotifier.xml` and in job `config.xml` files on the Jenkins controller as part of its configuration.

Additionally, they are transmitted in plain text as part of the respective configuration forms.

These API keys can be viewed by users with Item/Extended Read permission (job config.xml only) or access to the Jenkins controller file system (both).

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34803
- https://github.com/jenkinsci/opsgenie-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-1877
