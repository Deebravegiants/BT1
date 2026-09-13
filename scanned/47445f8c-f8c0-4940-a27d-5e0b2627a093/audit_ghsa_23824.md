# [M] Incorrect permission checks in Jenkins Matrix Authorization Strategy Plugin may allow accessing some items

## Summary
Severity: Medium
Advisory: GHSA-96jw-3xw4-mq9p
CVE: CVE-2021-21623
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-96jw-3xw4-mq9p
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:matrix-auth` — affected >=0 <2.6.6

## Details
Items (like jobs) can be organized hierarchically in Jenkins, using the Folders Plugin or something similar. An item is expected to be accessible only if all its ancestors are accessible as well.

Matrix Authorization Strategy Plugin 2.6.5 and earlier does not correctly perform permission checks to determine whether an item should be accessible.

This allows attackers with Item/Read permission on nested items to access them, even if they lack Item/Read permission for parent folders.\n\nMatrix Authorization Strategy Plugin 2.6.6 requires Item/Read permission on parent items to grant Item/Read permission on an individual item.

As a workaround in older releases, do not grant permissions on individual items to users who do not have access to parent items.

In case of problems, the [Java system property](https://www.jenkins.io/doc/book/managing/system-properties/) `hudson.security.AuthorizationMatrixProperty.checkParentPermissions` can be set to false, completely disabling this fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21623
- https://github.com/jenkinsci/matrix-auth-plugin/commit/bbe358575155912b818ab3c6e8b9623f21ad3418
- https://github.com/jenkinsci/matrix-auth-plugin
- https://www.jenkins.io/security/advisory/2021-03-18/#SECURITY-2180
- http://www.openwall.com/lists/oss-security/2021/03/18/5
