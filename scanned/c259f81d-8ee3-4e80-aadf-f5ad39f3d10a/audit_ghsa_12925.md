# [H] Sandbox bypass in Jenkins Script Security Plugin

## Summary
Severity: High
Advisory: GHSA-76qj-9gwh-pvv3
CVE: CVE-2023-24422
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-76qj-9gwh-pvv3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1229.v4880b

## Details
A sandbox bypass vulnerability involving map constructors in Jenkins Script Security Plugin 1228.vd93135a_2fb_25 and earlier allows attackers with permission to define and run sandboxed scripts, including Pipelines, to bypass the sandbox protection and execute arbitrary code in the context of the Jenkins controller JVM.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24422
- https://github.com/jenkinsci/script-security-plugin/commit/4880bbe905a6783d80150c8b881d0127430d4a73
- https://github.com/jenkinsci/script-security-plugin
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-3016
