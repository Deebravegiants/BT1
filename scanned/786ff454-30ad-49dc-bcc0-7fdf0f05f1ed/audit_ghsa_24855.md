# [H] AWS CodeDeploy Plugin stored AWS Secret Key in plain text

## Summary
Severity: High
Advisory: GHSA-h66p-m766-33fv
CVE: CVE-2018-1000403
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-h66p-m766-33fv
Type: github-advisory

## Affected
- Maven: `com.amazonaws:codedeploy` — affected >=0 <1.20

## Details
Jenkins project Jenkins AWS CodeDeploy Plugin version 1.19 and earlier contains a Insufficiently Protected Credentials vulnerability in AWSCodeDeployPublisher.java that can result in Credentials Disclosure. This attack appears to be exploitable via local file access. 

AWS CodeDeploy Plugin 1.20 and newer stores the AWS Secret Key encrypted in the configuration files on disk and no longer transfers it to users viewing the configuration form in plain text. Existing jobs need to have their configuration saved for existing plain text secret keys to be overwritten.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000403
- https://github.com/jenkinsci/aws-codedeploy-plugin
- https://jenkins.io/security/advisory/2018-06-25/#SECURITY-833
