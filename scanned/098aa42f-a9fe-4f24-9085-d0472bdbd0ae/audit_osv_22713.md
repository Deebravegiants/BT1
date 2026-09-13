# [M] CVE-2022-36893

## Summary
Severity: Medium
Advisory: CVE-2022-36893
Aliases: GHSA-pw4g-jcp5-63m9
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-07-27
Source: https://osv.dev/vulnerability/CVE-2022-36893
Type: osv

## Details
Jenkins rpmsign-plugin Plugin 0.5.0 and earlier does not perform a permission check in a method implementing form validation, allowing attackers with Item/Read permission but without Item/Workspace or Item/Configure permission to check whether attacker-specified file patterns match workspace contents.

## References
- http://www.openwall.com/lists/oss-security/2022/07/27/1
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2403
