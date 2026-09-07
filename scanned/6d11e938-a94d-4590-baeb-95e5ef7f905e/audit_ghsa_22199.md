# [M] Cleartext Transmission of Sensitive Information in Jenkins Configuration as Code Plugin

## Summary
Severity: Medium
Advisory: GHSA-r69h-6c4g-63xf
CVE: CVE-2019-10363
CWE: CWE-311, CWE-319
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r69h-6c4g-63xf
Type: github-advisory

## Affected
- Maven: `io.jenkins:configuration-as-code` — affected >=0 <1.25

## Details
Jenkins Configuration as Code Plugin 1.24 and earlier did not reliably identify sensitive values expected to be exported in their encrypted form.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10363
- https://github.com/jenkinsci/configuration-as-code-plugin/commit/7506d50b846460ec9f4506f0e228d2e44f0d5a3e
- https://jenkins.io/security/advisory/2019-07-31/#SECURITY-1458
- http://www.openwall.com/lists/oss-security/2019/07/31/1
