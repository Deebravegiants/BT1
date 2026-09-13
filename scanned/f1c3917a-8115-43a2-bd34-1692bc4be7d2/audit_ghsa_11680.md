# [H] Jenkins has a DNS rebinding vulnerability in WebSocket CLI origin validation

## Summary
Severity: High
Advisory: GHSA-phhv-63fh-rrc8
CVE: CVE-2026-33002
CWE: CWE-346, CWE-350
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-phhv-63fh-rrc8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.442 <2.555

## Details
Jenkins 2.442 through 2.554 (both inclusive), LTS 2.426.3 through LTS 2.541.2 (both inclusive) performs origin validation of requests made through the CLI WebSocket endpoint by computing the expected origin for comparison using the Host or X-Forwarded-Host HTTP request headers, making it vulnerable to DNS rebinding attacks that allow bypassing origin validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33002
- https://github.com/jenkinsci/jenkins/commit/348666da7136ef8270f88c0a7350562b0ba7f8ce
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2026-03-18/#SECURITY-3674
