# [M] BIT-mattermost-2023-50333

## Summary
Severity: Medium
Advisory: BIT-mattermost-2023-50333
Aliases: CVE-2023-50333, GHSA-9w97-9rqx-8v4j, GO-2024-2444
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-50333
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=0 <8.1.7

## Details
Mattermost fails to update the permissions of the current session for a user who was just demoted to guest, allowing freshly demoted guests to change group names.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2023-50333
