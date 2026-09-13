# [M] CVE-2019-10352

## Summary
Severity: Medium
Advisory: CVE-2019-10352
Aliases: GHSA-qr42-82qj-mw65
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-07-17
Source: https://osv.dev/vulnerability/CVE-2019-10352
Type: osv

## Details
A path traversal vulnerability in Jenkins 2.185 and earlier, LTS 2.176.1 and earlier in core/src/main/java/hudson/model/FileParameterValue.java allowed attackers with Job/Configure permission to define a file parameter with a file name outside the intended directory, resulting in an arbitrary file write on the Jenkins master when scheduling a build.

## References
- http://www.openwall.com/lists/oss-security/2019/07/17/2
- http://www.securityfocus.com/bid/109299
- https://access.redhat.com/errata/RHSA-2019:2503
- https://access.redhat.com/errata/RHSA-2019:2548
- https://jenkins.io/security/advisory/2019-07-17/#SECURITY-1424
- https://www.tenable.com/security/research/tra-2019-35
