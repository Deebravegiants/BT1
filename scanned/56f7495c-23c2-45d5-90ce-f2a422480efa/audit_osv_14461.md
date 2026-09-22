# [H] CVE-2019-1003004

## Summary
Severity: High
Advisory: CVE-2019-1003004
Aliases: GHSA-8qxp-g8jv-p37x
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-22
Source: https://osv.dev/vulnerability/CVE-2019-1003004
Type: osv

## Details
An improper authorization vulnerability exists in Jenkins 2.158 and earlier, LTS 2.150.1 and earlier in core/src/main/java/hudson/security/AuthenticationProcessingFilter2.java that allows attackers to extend the duration of active HTTP sessions indefinitely even though the user account may have been deleted in the mean time.

## References
- http://www.securityfocus.com/bid/106680
- https://access.redhat.com/errata/RHBA-2019:0327
- https://jenkins.io/security/advisory/2019-01-16/#SECURITY-901
