# [H] Jenkins Convert To Pipeline Plugin vulnerable to command injection

## Summary
Severity: High
Advisory: GHSA-7c44-m589-36w7
CVE: CVE-2023-28677
CWE: CWE-77
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-02
Source: https://github.com/advisories/GHSA-7c44-m589-36w7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:convert-to-pipeline` — affected >=0

## Details
Jenkins Convert To Pipeline Plugin 1.0 and earlier uses basic string concatenation to convert Freestyle projects' Build Environment, Build Steps, and Post-build Actions to the equivalent Pipeline step invocations.

This allows attackers able to configure Freestyle projects to prepare a crafted configuration that injects Pipeline script code into the (unsandboxed) Pipeline resulting from a conversion by Convert To Pipeline Plugin. If an administrator converts the Freestyle project to a Pipeline, the script will be pre-approved.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28677
- https://github.com/jenkinsci/convert-to-pipeline-plugin
- https://www.jenkins.io/security/advisory/2023-03-21/#SECURITY-2966
