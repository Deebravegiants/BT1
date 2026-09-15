# [M] Users with Overall/Read access could enumerate credentials IDs in Jenkins Fortify on Demand Plugin

## Summary
Severity: Medium
Advisory: GHSA-fph2-fwjq-prjf
CVE: CVE-2020-2202
CWE: CWE-285, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fph2-fwjq-prjf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:fortify-on-demand-uploader` — affected >=0 <6.0.1

## Details
Fortify on Demand Plugin provides a list of applicable credentials IDs to allow users configuring the plugin to select the one to use.

This functionality does not correctly check permissions in Fortify on Demand Plugin 6.0.0 and earlier, allowing any user with Overall/Read permission to get a list of valid credentials IDs. Those can be used as part of an attack to capture the credentials using another vulnerability.

An enumeration of credentials IDs in Fortify on Demand Plugin 6.0.1 now requires the appropriate permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2202
- https://github.com/jenkinsci/fortify-on-demand-uploader-plugin/commit/28932f7c5ff18f87d4b3a480225fb0827591776b
- https://github.com/jenkinsci/fortify-on-demand-uploader-plugin
- https://jenkins.io/security/advisory/2020-07-02/#SECURITY-1690
- http://www.openwall.com/lists/oss-security/2020/07/02/7
