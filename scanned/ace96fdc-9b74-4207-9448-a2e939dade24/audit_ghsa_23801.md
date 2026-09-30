# [H] RCE vulnerability in Jenkins Pipeline: AWS Steps Plugin

## Summary
Severity: High
Advisory: GHSA-w598-25hm-jqx3
CVE: CVE-2020-2166
CWE: CWE-20, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w598-25hm-jqx3
Type: github-advisory

## Affected
- Maven: `de.taimos:pipeline-aws` — affected >=0 <1.41

## Details
Pipeline: AWS Steps Plugin 1.40 and earlier does not configure its YAML parser to prevent the instantiation of arbitrary types. This results in a remote code execution (RCE) vulnerability exploitable by users able to provide YAML input files to Pipeline: AWS Steps Plugin’s build steps.

Pipeline: AWS Steps Plugin 1.41 configures its YAML parser to only instantiate safe types.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2166
- https://github.com/jenkinsci/pipeline-aws-plugin
- https://jenkins.io/security/advisory/2020-03-25/#SECURITY-1741
- http://www.openwall.com/lists/oss-security/2020/03/25/2
