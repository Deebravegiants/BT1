# [M] CVE-2018-1000862

## Summary
Severity: Medium
Advisory: CVE-2018-1000862
Aliases: GHSA-hph9-9vcq-f7gp
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-12-10
Source: https://osv.dev/vulnerability/CVE-2018-1000862
Type: osv

## Details
An information exposure vulnerability exists in Jenkins 2.153 and earlier, LTS 2.138.3 and earlier in DirectoryBrowserSupport.java that allows attackers with the ability to control build output to browse the file system on agents running builds beyond the duration of the build using the workspace browser.

## References
- http://www.securityfocus.com/bid/106176
- https://access.redhat.com/errata/RHBA-2019:0024
- https://jenkins.io/security/advisory/2018-12-05/#SECURITY-904
