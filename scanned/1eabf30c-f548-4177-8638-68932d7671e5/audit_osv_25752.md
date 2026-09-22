# [H] Non-MFA account takeover via brute-force attack on weak password reset code in jumpserver

## Summary
Severity: High
Advisory: CVE-2023-43650
Aliases: GHSA-mwx4-8fwc-2xvw
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2023-09-27
Source: https://osv.dev/vulnerability/CVE-2023-43650
Type: osv

## Details
JumpServer is an open source bastion host. The verification code for resetting user's password is vulnerable to brute-force attacks due to the absence of rate limiting. JumpServer provides a feature allowing users to reset forgotten passwords. Affected users are sent a 6-digit verification code, ranging from 000000 to 999999, to facilitate the password reset. Although the code is only available in 1 minute, this window potentially allows for up to 1,000,000 validation attempts. This issue has been addressed in versions 2.28.20 and 3.7.1. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/43xxx/CVE-2023-43650.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-mwx4-8fwc-2xvw
- https://nvd.nist.gov/vuln/detail/CVE-2023-43650
- https://www.sonarsource.com/blog/diving-into-jumpserver-attackers-gateway-to-internal-networks-1-2
