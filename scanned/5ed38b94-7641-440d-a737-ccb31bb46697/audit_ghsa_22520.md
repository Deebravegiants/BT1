# [H] Jenkins AWS CodePipeline Plugin has Insufficiently Protected Credentials

## Summary
Severity: High
Advisory: GHSA-5gwq-4275-q4qc
CVE: CVE-2018-1000401
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5gwq-4275-q4qc
Type: github-advisory

## Affected
- Maven: `com.amazonaws:aws-codepipeline` — affected >=0 <0.37

## Details
Jenkins project Jenkins AWS CodePipeline Plugin version 0.36 and earlier contains a Insufficiently Protected Credentials vulnerability in AWSCodePipelineSCM.java that can result in Credentials Disclosure. This attack appear to be exploitable via local file access. This vulnerability appears to have been fixed in 0.37 and later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000401
- https://github.com/jenkinsci/aws-codepipeline-plugin/commit/a45d3dc52c8b6f49e813a2ee8b796f0302649c69
- https://jenkins.io/security/advisory/2018-06-25/#SECURITY-967
