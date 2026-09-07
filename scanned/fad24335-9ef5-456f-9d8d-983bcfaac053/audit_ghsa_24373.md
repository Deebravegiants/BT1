# [M] CSRF vulnerability in Jenkins Config File Provider Plugin allows deleting configuration files

## Summary
Severity: Medium
Advisory: GHSA-998m-f2x3-jjq4
CVE: CVE-2021-21644
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-998m-f2x3-jjq4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:config-file-provider` — affected >=0 <3.7.1

## Details
Jenkins Config File Provider Plugin 3.7.0 and earlier does not require POST requests for an HTTP endpoint, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to delete configuration files corresponding to an attacker-specified ID.

This is due to an incomplete fix of [SECURITY-938](https://www.jenkins.io/security/advisory/2018-09-25/#SECURITY-938).

Jenkins Config File Provider Plugin 3.7.1 requires POST requests for the affected HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21644
- https://github.com/jenkinsci/config-file-provider-plugin/commit/9ffc32379477c4395ab17ff19b04b9f1286ceedb
- https://github.com/jenkinsci/config-file-provider-plugin
- https://www.jenkins.io/security/advisory/2021-04-21/#SECURITY-2202
- http://www.openwall.com/lists/oss-security/2021/04/21/2
