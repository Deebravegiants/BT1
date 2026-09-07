# [H] CSRF vulnerability in Jenkins XebiaLabs XL Deploy Plugin allows capturing credentials

## Summary
Severity: High
Advisory: GHSA-38pm-74xc-phcw
CVE: CVE-2021-21665
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-38pm-74xc-phcw
Type: github-advisory

## Affected
- Maven: `com.xebialabs.deployit.ci:deployit-plugin` — affected >=0 <10.0.2

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins XebiaLabs XL Deploy Plugin 10.0.1 and earlier allows attackers to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing Username/password credentials stored in Jenkins.

Jenkins XebiaLabs XL Deploy Plugin 10.0.2 requires POST requests and Overall/Administer permission for the affected form validation method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21665
- https://github.com/jenkinsci/xldeploy-plugin
- https://www.jenkins.io/security/advisory/2021-06-10/#SECURITY-1982
- http://www.openwall.com/lists/oss-security/2021/06/10/14
