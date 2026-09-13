# [H] RCE vulnerability in Jenkins AWS SAM Plugin

## Summary
Severity: High
Advisory: GHSA-qrm8-cw73-r9w8
CVE: CVE-2020-2180
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qrm8-cw73-r9w8
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:aws-sam` — affected >=0 <1.2.3

## Details
AWS SAM Plugin 1.2.2 and earlier does not configure its YAML parser to prevent the instantiation of arbitrary types. This results in a remote code execution (RCE) vulnerability exploitable by users able to configure a job or control the contents of a previously configured \"AWS SAM deploy application\" build step’s YAML SAM template file (`template.yaml` or equivalent) file.

AWS SAM Plugin 1.2.3 configures its YAML parser to only instantiate safe types.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2180
- https://github.com/jenkinsci/aws-sam-plugin/commit/6ddcb029638b5af05df701a11139d6a6c015ab7e
- https://github.com/jenkinsci/aws-sam-plugin
- https://jenkins.io/security/advisory/2020-04-16/#SECURITY-1736
- http://www.openwall.com/lists/oss-security/2020/04/16/4
