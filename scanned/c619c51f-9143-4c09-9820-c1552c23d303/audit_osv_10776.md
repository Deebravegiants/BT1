# [M] CVE-2017-2611

## Summary
Severity: Medium
Advisory: CVE-2017-2611
Aliases: GHSA-3297-944x-j7x7
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2018-05-08
Source: https://osv.dev/vulnerability/CVE-2017-2611
Type: osv

## Details
Jenkins before versions 2.44, 2.32.2 is vulnerable to an insufficient permission check for periodic processes (SECURITY-389). The URLs /workspaceCleanup and /fingerprintCleanup did not perform permission checks, allowing users with read access to Jenkins to trigger these background processes (that are otherwise performed daily), possibly causing additional load on Jenkins master and agents.

## References
- http://www.securityfocus.com/bid/95956
- https://github.com/jenkinsci/jenkins/commit/97a61a9fe55f4c16168c123f98301a5173b9fa86
- https://jenkins.io/security/advisory/2017-02-01/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2611
