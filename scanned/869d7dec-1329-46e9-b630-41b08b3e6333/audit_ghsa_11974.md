# [H] Jenkins has a link following vulnerability allows arbitrary file creation

## Summary
Severity: High
Advisory: GHSA-r6qv-frpc-q66c
CVE: CVE-2026-33001
CWE: CWE-59, CWE-61
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-r6qv-frpc-q66c
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.555

## Details
Jenkins 2.554 and earlier, LTS 2.541.2 and earlier does not safely handle symbolic links during the extraction of .tar and .tar.gz archives, allowing crafted archives to write files to arbitrary locations on the filesystem, restricted only by file system access permissions of the user running Jenkins.
This can be exploited to deploy malicious scripts or plugins on the controller by attackers with Item/Configure permission, or able to control agent processes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33001
- https://github.com/jenkinsci/jenkins/commit/6dc99937605d5bddfeaae43a4cd14c2571e23adc
- https://github.com/jenkinsci/jenkins
- https://github.com/jenkinsci/jenkins/releases/tag/jenkins-2.555
- https://www.jenkins.io/security/advisory/2026-03-18/#SECURITY-3657
