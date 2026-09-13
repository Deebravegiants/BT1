# [M] CVE-2022-23106

## Summary
Severity: Medium
Advisory: CVE-2022-23106
Aliases: GHSA-fpj7-9xm6-8hgr
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-01-12
Source: https://osv.dev/vulnerability/CVE-2022-23106
Type: osv

## Details
Jenkins Configuration as Code Plugin 1.55 and earlier used a non-constant time comparison function when validating an authentication token allowing attackers to use statistical methods to obtain a valid authentication token.

## References
- http://www.openwall.com/lists/oss-security/2022/01/12/6
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-2141
