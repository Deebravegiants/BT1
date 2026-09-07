# [M] Violation Comments to GitLab Plugin has Insufficiently Protected Credentials

## Summary
Severity: Medium
Advisory: GHSA-3p8r-p4q5-mc44
CVE: CVE-2019-10416
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3p8r-p4q5-mc44
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:violation-comments-to-gitlab` — affected >=0 <2.29

## Details
Violation Comments to GitLab Plugin stored API tokens unencrypted in job `config.xml` files and its global configuration file `org.jenkinsci.plugins.jvctgl.ViolationsToGitLabGlobalConfiguration.xml` on the Jenkins controller. These credentials could be viewed by users with Extended Read permission, or access to the Jenkins controller file system.

Violation Comments to GitLab Plugin now stores these credentials encrypted. Existing jobs need to have their configuration saved for existing plain text credentials to be overwritten.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10416
- https://github.com/jenkinsci/violation-comments-to-gitlab-plugin/commit/e8237a803012bae7773d8bd10fe02e21892be3fe
- https://jenkins.io/security/advisory/2019-09-25/#SECURITY-1577
- http://www.openwall.com/lists/oss-security/2019/09/25/3
