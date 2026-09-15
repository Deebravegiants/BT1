# [M] DoS via custom post type for sysconsole plugin readers

## Summary
Severity: Medium
Advisory: CVE-2025-20033
Aliases: GHSA-2549-xh72-qrpm, GO-2025-3379
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-01-09
Source: https://osv.dev/vulnerability/CVE-2025-20033
Type: osv

## Details
Mattermost versions 10.2.0, 9.11.x <= 9.11.5, 10.0.x <= 10.0.3, 10.1.x <= 10.1.3 fail to properly validate post types, which allows attackers to deny service to users with the sysconsole_read_plugins permission via creating a post with the custom_pl_notification type and specific props.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/20xxx/CVE-2025-20033.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-20033
