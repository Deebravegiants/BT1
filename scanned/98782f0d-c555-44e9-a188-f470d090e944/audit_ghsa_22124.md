# [M] Jenkins OpenId Connect Authentication Plugin showed plain text client secret in configuration form

## Summary
Severity: Medium
Advisory: GHSA-3858-58w9-wpcg
CVE: CVE-2019-1003021
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3858-58w9-wpcg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:oic-auth` — affected >=0 <1.5

## Details
An exposure of sensitive information vulnerability exists in Jenkins OpenId Connect Authentication Plugin 1.4 and earlier in OicSecurityRealm/config.jelly that allows attackers able to view a Jenkins administrator's web browser output, or control the browser (e.g. malicious extension) to retrieve the configured client secret.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003021
- https://jenkins.io/security/advisory/2019-01-28/#SECURITY-886
