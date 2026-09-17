# [M] Secrets are not masked by Jenkins Credentials Binding Plugin in builds without build steps

## Summary
Severity: Medium
Advisory: GHSA-43j2-r4v3-m8jp
CVE: CVE-2020-2181
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-43j2-r4v3-m8jp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:credentials-binding` — affected >=0 <1.23

## Details
Jenkins Credentials Binding Plugin 1.22 and earlier does not mask (i.e., replace with asterisks) secrets in the build log when the build contains no build steps.

Jenkins Credentials Binding Plugin 1.23 now masks secrets when the build contains no build steps.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2181
- https://github.com/jenkinsci/credentials-binding-plugin/commit/59ead11bcb3fd132258d1d7da4a34d47750f40d2
- https://github.com/jenkinsci/credentials-binding-plugin
- https://jenkins.io/security/advisory/2020-05-06/#SECURITY-1374
- http://www.openwall.com/lists/oss-security/2020/05/06/3
