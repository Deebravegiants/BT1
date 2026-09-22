# [M] CVE-2020-35236

## Summary
Severity: Medium
Advisory: CVE-2020-35236
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2020-12-14
Source: https://osv.dev/vulnerability/CVE-2020-35236
Type: osv

## Details
The GitLab Webhook Handler in amazee.io Lagoon before 1.12.3 has incorrect access control associated with project deletion.

## References
- https://github.com/amazeeio/lagoon/compare/v1.12.2...v1.12.3
- https://github.com/amazeeio/lagoon/tree/master/services/webhook-handler
- https://github.com/amazeeio/lagoon/tree/master/services/webhooks2tasks
- https://github.com/amazeeio/lagoon/commit/1140289bf9fa98b8602ab4662ae867b210d8476b
