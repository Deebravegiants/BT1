# [H] RCE vulnerability in Google Kubernetes Engine Plugin

## Summary
Severity: High
Advisory: GHSA-wf76-qgqq-gcfj
CVE: CVE-2020-2121
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wf76-qgqq-gcfj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:google-kubernetes-engine` — affected >=0 <0.8.1

## Details
Google Kubernetes Engine Plugin 0.8.0 and earlier does not configure its YAML parser to prevent the instantiation of arbitrary types. This results in a remote code execution vulnerability exploitable by users able to provide YAML input files to Google Kubernetes Engine Plugin’s build step.

Google Kubernetes Engine Plugin 0.8.1 configures its YAML parser to only instantiate safe types.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2121
- https://github.com/jenkinsci/google-kubernetes-engine-plugin
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1731
- http://www.openwall.com/lists/oss-security/2020/02/12/3
