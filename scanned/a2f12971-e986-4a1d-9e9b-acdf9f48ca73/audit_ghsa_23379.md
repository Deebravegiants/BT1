# [H] RCE vulnerability in Jenkins OpenShift Pipeline Plugin

## Summary
Severity: High
Advisory: GHSA-264w-xrr7-6qqg
CVE: CVE-2020-2167
CWE: CWE-20, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-264w-xrr7-6qqg
Type: github-advisory

## Affected
- Maven: `com.openshift.jenkins:openshift-pipeline` — affected >=0 <1.0.57

## Details
OpenShift Pipeline Plugin 1.0.56 and earlier does not configure its YAML parser to prevent the instantiation of arbitrary types. This results in a remote code execution (RCE) vulnerability exploitable by users able to provide YAML input files to OpenShift Pipeline Plugin’s build step. OpenShift Pipeline Plugin 1.0.57 configures its YAML parser to only instantiate safe types.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2167
- https://github.com/jenkinsci/openshift-pipeline-plugin
- https://jenkins.io/security/advisory/2020-03-25/#SECURITY-1739
- http://www.openwall.com/lists/oss-security/2020/03/25/2
