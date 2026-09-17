# [M] CVE-2017-2606

## Summary
Severity: Medium
Advisory: CVE-2017-2606
Aliases: GHSA-6967-9vvv-4cmm
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-05-08
Source: https://osv.dev/vulnerability/CVE-2017-2606
Type: osv

## Details
Jenkins before versions 2.44, 2.32.2 is vulnerable to an information exposure in the internal API that allows access to item names that should not be visible (SECURITY-380). This only affects anonymous users (other users legitimately have access) that were able to get a list of items via an UnprotectedRootAction.

## References
- http://www.securityfocus.com/bid/95962
- https://github.com/jenkinsci/jenkins/commit/09cfbc9cd5c9df7c763bc976b7f5c51266b63719
- https://jenkins.io/security/advisory/2017-02-01/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2606
