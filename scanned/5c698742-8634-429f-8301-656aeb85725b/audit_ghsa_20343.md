# [M] Cross-Site Request Forgery in Jenkins vRealize Orchestrator Plugin

## Summary
Severity: Medium
Advisory: GHSA-c965-p3w4-835c
CVE: CVE-2022-34211
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-c965-p3w4-835c
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:vmware-vrealize-orchestrator` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins vRealize Orchestrator Plugin 3.0 and earlier allows attackers to send an HTTP POST request to an attacker-specified URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34211
- https://github.com/jenkinsci/vmware-vrealize-orchestrator-plugin
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2279
