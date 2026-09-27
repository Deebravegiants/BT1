# [M] Mattermost Playbooks exposes private channel metadata to unauthorized users via run metadata API

## Summary
Severity: Medium
Advisory: CVE-2025-47871
Aliases: GHSA-wgvp-jj4w-88hf, GO-2025-3797
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-06-30
Source: https://osv.dev/vulnerability/CVE-2025-47871
Type: osv

## Details
Mattermost versions 10.5.x <= 10.5.5, 9.11.x <= 9.11.15, 10.8.x <= 10.8.0, 10.7.x <= 10.7.2, 10.6.x <= 10.6.5 fail to properly validate channel membership when retrieving playbook run metadata, allowing authenticated users who are playbook members but not channel members to access sensitive information about linked private channels including channel name, display name, and participant count through the run metadata API endpoint.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47871.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-47871
