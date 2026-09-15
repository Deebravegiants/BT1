# [H] CVE-2018-1000863

## Summary
Severity: High
Advisory: CVE-2018-1000863
Aliases: GHSA-4jhm-5f7g-75fp
CVSS: 8.2 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2018-12-10
Source: https://osv.dev/vulnerability/CVE-2018-1000863
Type: osv

## Details
A data modification vulnerability exists in Jenkins 2.153 and earlier, LTS 2.138.3 and earlier in User.java, IdStrategy.java that allows attackers to submit crafted user names that can cause an improper migration of user record storage formats, potentially preventing the victim from logging into Jenkins.

## References
- http://www.securityfocus.com/bid/106176
- https://access.redhat.com/errata/RHBA-2019:0024
- https://jenkins.io/security/advisory/2018-12-05/#SECURITY-1072
- https://www.tenable.com/security/research/tra-2018-43
