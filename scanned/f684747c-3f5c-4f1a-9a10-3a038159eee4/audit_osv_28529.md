# [M] Playbook Run Metadata leak to Guest

## Summary
Severity: Medium
Advisory: CVE-2024-34152
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-05-26
Source: https://osv.dev/vulnerability/CVE-2024-34152
Type: osv

## Details
Mattermost versions 9.5.x <= 9.5.3, 9.6.x <= 9.6.1 and 8.1.x <= 8.1.12 fail to perform proper access control which allows a guest to get the metadata of a public playbook run that linked to the channel they are guest via sending an RHSRuns GraphQL query request to the server

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34152.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34152
