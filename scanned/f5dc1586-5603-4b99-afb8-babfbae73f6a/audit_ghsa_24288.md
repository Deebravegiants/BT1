# [H] CSRF vulnerability in Jenkins Build With Parameters Plugin

## Summary
Severity: High
Advisory: GHSA-w24g-24qg-v4w2
CVE: CVE-2021-21629
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w24g-24qg-v4w2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:build-with-parameters` — affected >=0 <1.5.1

## Details
Jenkins Build With Parameters Plugin 1.5 and earlier does not require POST requests for its form submission endpoint, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to build a project with attacker-specified parameters. Build With Parameters Plugin 1.5.1 requires POST requests for the affected HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21629
- https://github.com/jenkinsci/build-with-parameters-plugin/commit/82711e83bf822c5688017304939d5d1c3482ec3e
- https://github.com/jenkinsci/build-with-parameters-plugin
- https://www.jenkins.io/security/advisory/2021-03-30/#SECURITY-2257
- http://www.openwall.com/lists/oss-security/2021/03/30/1
