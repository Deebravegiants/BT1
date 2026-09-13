# [M] Jenkins Subversion Partial Release Manager Plugin programmatically disables the fix for CVE-2016-3721 

## Summary
Severity: Medium
Advisory: GHSA-phh3-2p9m-w6j5
CVE: CVE-2024-34148
CWE: CWE-1321
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-05-02
Source: https://github.com/advisories/GHSA-phh3-2p9m-w6j5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:partial-release-manager` — affected >=0

## Details
Jenkins Subversion Partial Release Manager Plugin 1.0.1 and earlier programmatically sets the Java system property `hudson.model.ParametersAction.keepUndefinedParameters` whenever a build is triggered from a release tag with the 'Svn-Partial Release Manager' SCM. Doing so disables the fix for [SECURITY-170](https://www.jenkins.io/security/advisory/2016-05-11/#arbitrary-build-parameters-are-passed-to-build-scripts-as-environment-variables) / CVE-2016-3721.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34148
- https://www.jenkins.io/security/advisory/2024-05-02/#SECURITY-3331
- http://www.openwall.com/lists/oss-security/2024/05/02/3
