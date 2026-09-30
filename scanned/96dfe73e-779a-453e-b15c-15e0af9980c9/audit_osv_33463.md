# [M] Slack import bypasses email verification for team access controls

## Summary
Severity: Medium
Advisory: CVE-2025-41410
Aliases: GHSA-3q4q-wqm6-hvf3, GO-2025-4029
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-41410
Type: osv

## Details
Mattermost versions 10.10.x <= 10.10.2, 10.5.x <= 10.5.10, 10.11.x <= 10.11.2 fail to validate email ownership during Slack import process which allows attackers to create verified user accounts with arbitrary email domains via malicious Slack import data to bypass email-based team access restrictions

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/41xxx/CVE-2025-41410.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-41410
