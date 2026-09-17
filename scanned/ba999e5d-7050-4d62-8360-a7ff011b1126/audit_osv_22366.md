# [M] CVE-2022-27201

## Summary
Severity: Medium
Advisory: CVE-2022-27201
Aliases: GHSA-x3m3-g8w6-mf28
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-03-15
Source: https://osv.dev/vulnerability/CVE-2022-27201
Type: osv

## Details
Jenkins Semantic Versioning Plugin 1.13 and earlier does not restrict execution of an controller/agent message to agents, and implements no limitations about the file path that can be parsed, allowing attackers able to control agent processes to have Jenkins parse a crafted file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

## References
- http://www.openwall.com/lists/oss-security/2022/03/15/2
- https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-2124
