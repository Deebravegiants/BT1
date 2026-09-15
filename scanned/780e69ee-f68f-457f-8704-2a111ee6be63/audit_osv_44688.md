# [M] MISP Attribute Deletion Authorization Bypass Allows Users Without Modify Permissions to Delete Attributes

## Summary
Severity: Medium
Advisory: CVE-2026-85538
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:H/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85538
Type: osv

## Details
An incorrect authorization vulnerability in MISP allowed authenticated users to delete attributes from events despite lacking the required perm_modify or perm_modify_org permissions.

The affected attribute deletion paths relied on organization membership checks performed by MispAttribute::deleteAttribute() but did not consistently enforce MISP's event modification authorization rules. Consequently, a user belonging to the organization associated with an event could potentially delete individual attributes or perform bulk attribute deletion even when their assigned role was not authorized to modify the event.

This created an inconsistency between attribute editing and deletion: editing an attribute correctly used MISP's ACL::canModifyEvent() authorization logic, whereas the affected deletion operations could bypass these permission checks.

An authenticated attacker with access to an affected MISP instance and membership in the organization owning an event could exploit this flaw to remove attributes from that event, potentially causing unauthorized modification or loss of threat intelligence data.

The patch introduces a common authorization check for all affected deletion paths. Before deletion, MISP now resolves the associated events and verifies that the current user is authorized to modify each event using the same authorization mechanism used by normal event and attribute modification operations.

## References
- https://github.com/MISP/MISP/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85538.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85538
- https://github.com/MISP/MISP/commit/d0a6f963f
