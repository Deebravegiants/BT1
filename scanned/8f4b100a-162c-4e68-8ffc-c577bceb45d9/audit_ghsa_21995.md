# [H] Stored Cross-site Scripting vulnerability in Jenkins Agent Server Parameter Plugin

## Summary
Severity: High
Advisory: GHSA-53c4-cmhf-gp7w
CVE: CVE-2022-25191
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-53c4-cmhf-gp7w
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:agent-server-parameter` — affected >=0 <1.1

## Details
Jenkins Agent Server Parameter Plugin 1.0 and earlier does not escape parameter names of agent server parameters, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25191
- https://github.com/jenkinsci/agent-server-parameter-plugin/commit/cd237c40c76661b5c6a05e542034746e431e706e
- https://github.com/jenkinsci/agent-server-parameter-plugin
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2268
