# [M] SAML to email switch possible when email signin is disabled

## Summary
Severity: Medium
Advisory: CVE-2024-5270
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-05-26
Source: https://osv.dev/vulnerability/CVE-2024-5270
Type: osv

## Details
Mattermost versions 9.5.x <= 9.5.3, 9.7.x <= 9.7.1, 9.6.x <= 9.6.1 and 8.1.x <= 8.1.12 fail to check if the email signup configuration option is enabled when a user requests to switch from SAML to Email. This allows the user to switch their authentication mail from SAML to email and possibly edit personal details that were otherwise non-editable and provided by the SAML provider.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5270.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5270
