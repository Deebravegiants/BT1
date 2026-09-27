# [M] Passwords stored in plain text by Harvest SCM Plugin

## Summary
Severity: Medium
Advisory: GHSA-jmp9-f42q-4g85
CVE: CVE-2020-2130
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jmp9-f42q-4g85
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:harvest` — affected >=0

## Details
Harvest SCM Plugin 0.5.1 and earlier stores SCM passwords unencrypted in its global configuration file `hudson.plugins.harvest.HarvestSCM.xml and in job config.xml` files on the Jenkins controller. These credentials can be viewed by users with Extended Read permission (job config.xml only) or access to the Jenkins controller file system (both).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2130
- https://github.com/jenkinsci/harvest-plugin
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1553
- http://www.openwall.com/lists/oss-security/2020/02/12/3
