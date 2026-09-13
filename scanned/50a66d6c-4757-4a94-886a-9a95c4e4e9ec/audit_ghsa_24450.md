# [H] Insufficiently Protected Credentials in Jenkins AWS CodeBuild Plugin

## Summary
Severity: High
Advisory: GHSA-mwg7-69hf-vqh3
CVE: CVE-2018-1000404
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mwg7-69hf-vqh3
Type: github-advisory

## Affected
- Maven: `com.amazonaws:aws-codebuild` — affected >=0 <0.27

## Details
Jenkins project Jenkins AWS CodeBuild Plugin version 0.26 and earlier contains a Insufficiently Protected Credentials vulnerability in AWSClientFactory.java, CodeBuilder.java that can result in Credentials Disclosure. This attack appear to be exploitable via local file access. This vulnerability appears to have been fixed in 0.27 and later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000404
- https://github.com/jenkinsci/aws-codebuild-plugin/commit/f5bae399c245ff6a7131ce9cca9636f5971d582c
- https://jenkins.io/security/advisory/2018-06-25/#SECURITY-834
