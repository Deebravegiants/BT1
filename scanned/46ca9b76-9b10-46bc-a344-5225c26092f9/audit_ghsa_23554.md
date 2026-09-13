# [M] Jenkins Google Kubernetes Engine Plugin vulnerable to Exposure of Resource to Wrong Sphere

## Summary
Severity: Medium
Advisory: GHSA-xw4c-9434-3f7p
CVE: CVE-2019-10365
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xw4c-9434-3f7p
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:google-kubernetes-engine` — affected >=0 <0.6.3

## Details
Jenkins Google Kubernetes Engine Plugin 0.6.2 and earlier created a temporary file named `.kube…config` containing a temporary access token in the project workspace, where it could be accessed by users with Job/Read permission.

This temporary file is now created outside the regular project workspace.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10365
- https://jenkins.io/security/advisory/2019-07-31/#SECURITY-1345
- http://www.openwall.com/lists/oss-security/2019/07/31/1
