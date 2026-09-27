# [M] Mobile crash via improper validation of proto style in attachments

## Summary
Severity: Medium
Advisory: CVE-2025-20072
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-16
Source: https://osv.dev/vulnerability/CVE-2025-20072
Type: osv

## Details
Mattermost Mobile versions <= 2.22.0 fail to properly validate the style of proto supplied to an action's style in post.props.attachments, which allows an attacker to crash the mobile via crafted malicious input.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/20xxx/CVE-2025-20072.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-20072
