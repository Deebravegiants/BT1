# [M] CVE-2019-10305

## Summary
Severity: Medium
Advisory: CVE-2019-10305
Aliases: GHSA-44w7-gh9c-4qvr
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-04-18
Source: https://osv.dev/vulnerability/CVE-2019-10305
Type: osv

## Details
A missing permission check in Jenkins XebiaLabs XL Deploy Plugin in the Credential#doValidateUserNamePassword form validation method allows attackers with Overall/Read permission to initiate a connection to an attacker-specified server.

## References
- http://www.securityfocus.com/bid/108045
- https://jenkins.io/security/advisory/2019-04-17/#SECURITY-983
