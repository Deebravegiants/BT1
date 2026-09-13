# [M] Run Details leak to guest via webhook event "custom_playbooks_playbook_run_updated"

## Summary
Severity: Medium
Advisory: CVE-2024-5272
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-05-26
Source: https://osv.dev/vulnerability/CVE-2024-5272
Type: osv

## Details
Mattermost versions 9.5.x <= 9.5.3, 9.6.x <= 9.6.1, 8.1.x <= 8.1.12 fail to restrict the audience of the "custom_playbooks_playbook_run_updated" webhook event, which allows a guest on a channel with a playbook run linked to see all the details of the playbook run when the run is marked by finished.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5272.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5272
