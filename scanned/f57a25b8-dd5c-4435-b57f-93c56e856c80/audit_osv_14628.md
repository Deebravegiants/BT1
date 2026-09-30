# [M] CVE-2019-10342

## Summary
Severity: Medium
Advisory: CVE-2019-10342
Aliases: GHSA-745w-v492-4fj5
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-07-11
Source: https://osv.dev/vulnerability/CVE-2019-10342
Type: osv

## Details
A missing permission check in Jenkins Docker Plugin 1.1.6 and earlier in various 'fillCredentialsIdItems' methods allowed users with Overall/Read access to enumerate credentials ID of credentials stored in Jenkins.

## References
- http://www.openwall.com/lists/oss-security/2019/07/11/4
- http://www.securityfocus.com/bid/109156
- https://jenkins.io/security/advisory/2019-07-11/#SECURITY-1400
