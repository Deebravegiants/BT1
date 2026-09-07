# [M] Jenkins IBM Cloud DevOps Plugin vulnerability exposes SonarQube authentication tokens

## Summary
Severity: Medium
Advisory: GHSA-pgrx-5f8q-r5mq
CVE: CVE-2025-53663
CWE: CWE-311, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-pgrx-5f8q-r5mq
Type: github-advisory

## Affected
- Maven: `com.ibm.devops:ibm-cloud-devops` — affected >=0

## Details
Jenkins IBM Cloud DevOps Plugin 2.0.16 and earlier stores SonarQube authentication tokens unencrypted in job `config.xml` files on the Jenkins controller as part of its configuration.

These tokens can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53663
- https://github.com/jenkinsci/ibm-cloud-devops-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3552
- http://www.openwall.com/lists/oss-security/2025/07/09/4
