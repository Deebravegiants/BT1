# [M] Mattermost Playbooks allows privilege escalation through improper access control in playbook run participant management

## Summary
Severity: Medium
Advisory: CVE-2025-46702
Aliases: GHSA-v8fr-vxmw-6mf6, GO-2025-3796
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-06-30
Source: https://osv.dev/vulnerability/CVE-2025-46702
Type: osv

## Details
Mattermost versions 10.5.x <= 10.5.5, 9.11.x <= 9.11.15, 10.8.x <= 10.8.0, 10.7.x <= 10.7.2, 10.6.x <= 10.6.5 fail to properly enforce channel member management permissions when adding participants to playbook runs. This allows authenticated users with member-level permissions to bypass system admin restrictions and add or remove users to/from private channels via the playbook run participants feature, even when the 'Manage Members' permission has been explicitly removed. This can lead to unauthorized access to sensitive channel content and allow guest users to gain channel management privileges.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46702.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-46702
