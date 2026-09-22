# [C] CVE-2020-2300

## Summary
Severity: Critical
Advisory: CVE-2020-2300
Aliases: GHSA-8wcw-cw2f-h4g2
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-04
Source: https://osv.dev/vulnerability/CVE-2020-2300
Type: osv

## Details
Jenkins Active Directory Plugin 2.19 and earlier does not prohibit the use of an empty password in Windows/ADSI mode, which allows attackers to log in to Jenkins as any user depending on the configuration of the Active Directory server.

## References
- http://www.openwall.com/lists/oss-security/2020/11/04/6
- https://www.jenkins.io/security/advisory/2020-11-04/#SECURITY-2099
