# [M] CVE-2021-21624

## Summary
Severity: Medium
Advisory: CVE-2021-21624
Aliases: GHSA-rm4m-39fj-288c
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-03-18
Source: https://osv.dev/vulnerability/CVE-2021-21624
Type: osv

## Details
An incorrect permission check in Jenkins Role-based Authorization Strategy Plugin 3.1 and earlier allows attackers with Item/Read permission on nested items to access them, even if they lack Item/Read permission for parent folders.

## References
- http://www.openwall.com/lists/oss-security/2021/03/18/5
- https://www.jenkins.io/security/advisory/2021-03-18/#SECURITY-2182
