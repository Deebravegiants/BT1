# [M] SAML certificate deletion allows path traversal to delete arbitrary files outside the config directory

## Summary
Severity: Medium
Advisory: CVE-2026-7521
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/CVE-2026-7521
Type: osv

## Details
Mattermost versions 11.8.x <= 11.8.0, 11.7.x <= 11.7.3, 11.6.x <= 11.6.5, 10.11.x <= 10.11.20 fail to verify file deletion path which allows an admin with SAML system-console write permissions to delete arbitrary files outside the config directory from the server via the remove file endpoint.. Mattermost Advisory ID: MMSA-2026-00666

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7521.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-7521
