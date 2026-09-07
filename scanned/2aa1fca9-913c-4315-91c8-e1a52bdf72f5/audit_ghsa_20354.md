# [H] Reflected Cross site scripting in Jenkins Embeddable Build Status Plugin

## Summary
Severity: High
Advisory: GHSA-39r3-h8q6-2phq
CVE: CVE-2022-34178
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-39r3-h8q6-2phq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:embeddable-build-status` — affected >=0 <2.0.4

## Details
Jenkins Embeddable Build Status Plugin 2.0.3 allows specifying a 'link' query parameter that build status badges will link to, without restricting possible values, resulting in a reflected cross-site scripting (XSS) vulnerability.

Embeddable Build Status Plugin 2.0.4 limits URLs to `http` and `https` protocols and correctly escapes the provided value.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34178
- https://github.com/jenkinsci/embeddable-build-status-plugin/commit/0fc4a199506328b08dcd0aca572a2ca79ca38714
- https://github.com/jenkinsci/embeddable-build-status-plugin
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2567
