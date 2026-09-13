# [M] Jenkins Image Gallery Plugin allows Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-8xr3-54w2-8xjp
CVE: CVE-2016-4987
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8xr3-54w2-8xjp
Type: github-advisory

## Affected
- Maven: `com.tupilabs.image_gallery:image-gallery` — affected >=0 <1.4

## Details
Directory traversal vulnerability in the Image Gallery plugin before 1.4 in Jenkins allows remote attackers to list arbitrary directories and read arbitrary files via unspecified form fields.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4987
- https://github.com/jenkinsci/image-gallery-plugin/commit/20f02f6d53e642431d5e1181a8e7be7971538d50
- https://github.com/jenkinsci/image-gallery-plugin
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2016-06-20
