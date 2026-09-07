# [M] Jenkins Git Changelog Plugin has Insufficiently Protected Credentials

## Summary
Severity: Medium
Advisory: GHSA-h27g-72mh-9m33
CVE: CVE-2019-10414
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h27g-72mh-9m33
Type: github-advisory

## Affected
- Maven: `de.wellnerbou.jenkins:git-changelog` — affected >=0 <2.18

## Details
Git Changelog Plugin stored MediaWiki and Jira passwords unencrypted in job `config.xml` files on the Jenkins controller. These passwords could be viewed by users with Extended Read permission, or access to the Jenkins controller file system.

Git Changelog Plugin now stores these passwords encrypted. Existing jobs need to have their configuration saved for existing plain text passwords to be overwritten.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10414
- https://github.com/jenkinsci/git-changelog-plugin/commit/356243aa6d3f6ad60f057e7567a3466910618441
- https://github.com/jenkinsci/git-changelog-plugin
- https://jenkins.io/security/advisory/2019-09-25/#SECURITY-1574
- http://www.openwall.com/lists/oss-security/2019/09/25/3
