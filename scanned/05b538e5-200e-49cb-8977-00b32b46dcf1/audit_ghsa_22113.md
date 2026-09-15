# [H] Jenkins Support Core Plugin allowed users with Overall/Read permission to delete arbitrary files

## Summary
Severity: High
Advisory: GHSA-2cxg-448h-4wxj
CVE: CVE-2019-16540
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2cxg-448h-4wxj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:support-core` — affected >=0 <2.64

## Details
Jenkins Support Core Plugin did not validate the paths submitted for the "Delete Support Bundles" feature. This allowed users to delete arbitrary files on the Jenkins controller file system accessible to the OS user account running Jenkins.

Additionally, this endpoint did not perform a permission check, allowing users with Overall/Read permission to delete support bundles, and any arbitrary other file, with a known name/path.

Support Core Plugin now only allows the deletion of support bundles and related files listed on the UI through this feature. It also ensures that only users with "Download Bundle" permission are able to delete support bundles.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16540
- https://github.com/jenkinsci/support-core-plugin/commit/6b177ea7cc7347e13fa87174472400bbbe78d422
- https://github.com/jenkinsci/support-core-plugin
- https://jenkins.io/security/advisory/2019-11-21/#SECURITY-1634
- http://www.openwall.com/lists/oss-security/2019/11/21/1
