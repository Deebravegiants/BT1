# [M] CVE-2021-21663

## Summary
Severity: Medium
Advisory: CVE-2021-21663
Aliases: GHSA-6mpp-cm3v-23vv
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-06-10
Source: https://osv.dev/vulnerability/CVE-2021-21663
Type: osv

## Details
A missing permission check in Jenkins XebiaLabs XL Deploy Plugin 7.5.8 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing Username/password credentials stored in Jenkins.

## References
- http://www.openwall.com/lists/oss-security/2021/06/10/14
- https://www.jenkins.io/security/advisory/2021-06-10/#SECURITY-1982
