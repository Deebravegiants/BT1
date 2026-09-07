# [M] CSRF vulnerability in Jenkins Azure Service Fabric Plugin 

## Summary
Severity: Medium
Advisory: GHSA-wh3h-j8wp-6p42
CVE: CVE-2025-24402
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-01-22
Source: https://github.com/advisories/GHSA-wh3h-j8wp-6p42
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:service-fabric` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Azure Service Fabric Plugin 1.6 and earlier allows attackers to connect to a Service Fabric URL using attacker-specified credentials IDs obtained through another method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24402
- https://github.com/jenkinsci/service-fabric-plugin
- https://www.jenkins.io/security/advisory/2025-01-22/#SECURITY-3094
