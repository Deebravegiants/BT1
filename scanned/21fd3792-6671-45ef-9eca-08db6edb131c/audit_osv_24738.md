# [M] Missing brute force protection on password reset token in Nextcloud Server

## Summary
Severity: Medium
Advisory: CVE-2023-25818
Aliases: GHSA-v243-x6jc-42mp
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2023-25818
Type: osv

## Details
Nextcloud server is an open source, personal cloud implementation. In affected versions a malicious user could try to reset the password of another user and then brute force the 62^21 combinations for the password reset token. As of commit `704eb3aa` password reset attempts are now throttled. Note that 62^21 combinations would significant compute resources to brute force. None the less it is recommended that the Nextcloud Server is upgraded to 24.0.10 or 25.0.4. There are no known workarounds for this vulnerability.

## References
- https://github.com/nextcloud/server/pull/36489/commits/704eb3aa6cecc0a646f5cca4290b595f493f9ed3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25818.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-v243-x6jc-42mp
- https://nvd.nist.gov/vuln/detail/CVE-2023-25818
- https://github.com/nextcloud/server/pull/36489
