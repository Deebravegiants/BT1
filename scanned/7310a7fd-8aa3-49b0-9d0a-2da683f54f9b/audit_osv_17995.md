# [M] CVE-2020-2250

## Summary
Severity: Medium
Advisory: CVE-2020-2250
Aliases: GHSA-ccwp-633j-g29v
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-09-01
Source: https://osv.dev/vulnerability/CVE-2020-2250
Type: osv

## Details
Jenkins SoapUI Pro Functional Testing Plugin 1.3 and earlier stores project passwords unencrypted in job config.xml files on the Jenkins controller where they can be viewed by attackers with Extended Read permission, or access to the Jenkins controller file system.

## References
- http://www.openwall.com/lists/oss-security/2020/09/01/3
- https://jenkins.io/security/advisory/2020-09-01/#SECURITY-1631%20%281%29
