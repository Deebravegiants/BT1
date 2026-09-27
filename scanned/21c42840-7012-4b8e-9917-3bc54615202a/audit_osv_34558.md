# [H] GraphQL IDOR allows authenticated user to delete workspace content of other users

## Summary
Severity: High
Advisory: CVE-2025-61781
Aliases: GHSA-pr6m-q4g7-342c, PYSEC-2026-116
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-01-05
Source: https://osv.dev/vulnerability/CVE-2025-61781
Type: osv

## Details
OpenCTI is an open source platform for managing cyber threat intelligence knowledge and observables. Prior to version 6.8.1, the GraphQL mutation "WorkspacePopoverDeletionMutation" allows users to delete workspace-related objects such as dashboards and investigation cases. However, the mutation lacks proper authorization checks to verify ownership of the targeted resources.
An attacker can exploit this by supplying an active UUID of another user. Since the API does not validate whether the requester owns the resource, the mutation executes successfully, resulting in unauthorized deletion of the entire workspace. Version 6.8.1 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61781.json
- https://github.com/OpenCTI-Platform/opencti/security/advisories/GHSA-pr6m-q4g7-342c
- https://nvd.nist.gov/vuln/detail/CVE-2025-61781
