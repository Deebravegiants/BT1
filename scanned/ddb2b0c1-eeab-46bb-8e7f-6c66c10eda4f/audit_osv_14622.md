# [M] CVE-2019-10323

## Summary
Severity: Medium
Advisory: CVE-2019-10323
Aliases: GHSA-3m8w-442m-3p2q
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-05-31
Source: https://osv.dev/vulnerability/CVE-2019-10323
Type: osv

## Details
A missing permission check in Jenkins Artifactory Plugin 3.2.3 and earlier in various 'fillCredentialsIdItems' methods allowed users with Overall/Read access to enumerate credentials ID of credentials stored in Jenkins.

## References
- http://www.openwall.com/lists/oss-security/2019/05/31/2
- http://www.securityfocus.com/bid/108540
- https://jenkins.io/security/advisory/2019-05-31/#SECURITY-1015%20%282%29
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2019-0846
