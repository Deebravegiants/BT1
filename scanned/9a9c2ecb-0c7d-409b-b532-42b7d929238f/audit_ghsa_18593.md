# [M] Jenkins OpenShift Pipeline Plugin stores authorization tokens unencrypted in job config.xml files

## Summary
Severity: Medium
Advisory: GHSA-4653-9q2r-684q
CVE: CVE-2025-64143
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-4653-9q2r-684q
Type: github-advisory

## Affected
- Maven: `com.openshift.jenkins:openshift-pipeline` — affected >=0

## Details
Jenkins OpenShift Pipeline Plugin 1.0.57 and earlier stores authorization tokens unencrypted in job `config.xml` files on the Jenkins controller as part of its configuration.

These token can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-64143
- https://github.com/jenkinsci/openshift-pipeline-plugin
- https://www.jenkins.io/security/advisory/2025-10-29/#SECURITY-3553
- http://www.openwall.com/lists/oss-security/2025/10/29/2
