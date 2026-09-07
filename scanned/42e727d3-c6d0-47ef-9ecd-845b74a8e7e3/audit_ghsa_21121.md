# [H] Missing Authorization in Jenkins Recipe Plugin

## Summary
Severity: High
Advisory: GHSA-j33r-cgm6-pv48
CVE: CVE-2022-34794
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-j33r-cgm6-pv48
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:recipe` — affected >=0

## Details
Missing permission checks in Jenkins Recipe Plugin 1.2 and earlier allow attackers with Overall/Read permission to send an HTTP request to an attacker-specified URL and parse the response as XML.

Additionally, the plugin allows users to export the full configuration of jobs as part of a recipe, granting access to job configuration XML data to every user with Item/Read permission. The encrypted values of secrets stored in the job configuration are not redacted, as they would be by the config.xml API for users without Item/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34794
- https://github.com/jenkinsci/recipe-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2000
