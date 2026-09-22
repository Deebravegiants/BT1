# [M] Users with Overall/Read access can enumerate credential IDs in Pipeline GitHub Notify Step Plugin

## Summary
Severity: Medium
Advisory: GHSA-8p4m-62gp-33j4
CVE: CVE-2020-2118
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8p4m-62gp-33j4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:pipeline-build-step` — affected >=0 <1.0.5

## Details
Pipeline GitHub Notify Step Plugin 1.0.4 and earlier provides a list of applicable credential IDs to allow users configuring the plugin to select the one to use.

This functionality does not correctly check permissions, allowing any user with Overall/Read permission to get a list of valid credentials IDs. Those can be used as part of an attack to capture the credentials using another vulnerability.

An enumeration of credentials IDs in Pipeline GitHub Notify Step Plugin 1.0.5 requires the permission to configure a project.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2118
- https://github.com/jenkinsci/pipeline-githubnotify-step-plugin
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-812%20(2)
- http://www.openwall.com/lists/oss-security/2020/02/12/3
