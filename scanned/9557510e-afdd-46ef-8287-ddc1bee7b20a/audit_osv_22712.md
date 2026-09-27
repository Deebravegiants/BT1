# [M] CVE-2022-36885

## Summary
Severity: Medium
Advisory: CVE-2022-36885
Aliases: GHSA-mxcc-7h5m-x57r
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-07-27
Source: https://osv.dev/vulnerability/CVE-2022-36885
Type: osv

## Details
Jenkins GitHub Plugin 1.34.4 and earlier uses a non-constant time comparison function when checking whether the provided and computed webhook signatures are equal, allowing attackers to use statistical methods to obtain a valid webhook signature.

## References
- http://www.openwall.com/lists/oss-security/2022/07/27/1
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-1849
