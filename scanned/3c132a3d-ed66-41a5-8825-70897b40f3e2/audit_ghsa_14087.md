# [M] Jenkins Ansible Plugin stores and displays secrets in plain text

## Summary
Severity: Medium
Advisory: GHSA-38hw-368m-7jmg
CVE: CVE-2023-32982
CWE: CWE-311, CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-38hw-368m-7jmg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ansible` — affected >=0 <205.v4cb

## Details
Jenkins Ansible Plugin allows the specification of extra variables that can be passed to Ansible. These extra variables are commonly used to pass secrets.

Ansible Plugin 204.v8191fd551eb_f and earlier stores these extra variables unencrypted in job config.xml files on the Jenkins controller as part of its configuration.

These extra variables can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

Additionally, the job configuration form does not mask these extra variables, increasing the potential for attackers to observe and capture them.

Ansible Plugin 205.v4cb_c48657c21 masks extra variables displayed on the configuration form, and stores them encrypted once job configurations are saved again.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32982
- https://github.com/jenkinsci/ansible-plugin/commit/4cbc48657c21a65a917b3b3049918480198c0cfb
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-3017
