# [M] Incorrect permission check in XebiaLabs XL Deploy Plugin allows capturing credentials

## Summary
Severity: Medium
Advisory: GHSA-jm4g-8rvq-v87j
CVE: CVE-2021-21664
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jm4g-8rvq-v87j
Type: github-advisory

## Affected
- Maven: `com.xebialabs.deployit.ci:deployit-plugin` — affected >=0 <10.0.2

## Details
An incorrect permission check in Jenkins XebiaLabs XL Deploy Plugin 10.0.1 and earlier allows attackers with Generic Create permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing Username/password credentials stored in Jenkins.

The permission check was partially fixed in XebiaLabs XL Deploy Plugin 7.5.9: A permission check was added, but for the wrong permission, still allowing some non-admin users to access the form validation method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21664
- https://github.com/jenkinsci/xldeploy-plugin/commit/79ae204d2ee6cd94badf4c24a150cee13a3bde44
- https://github.com/jenkinsci/xldeploy-plugin
- https://www.jenkins.io/security/advisory/2021-06-10/#SECURITY-1982
- http://www.openwall.com/lists/oss-security/2021/06/10/14
