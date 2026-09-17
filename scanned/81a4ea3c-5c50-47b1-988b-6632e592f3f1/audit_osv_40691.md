# [M] MISP mass assignment vulnerabilities allow unauthorized modification of ownership and delegation records

## Summary
Severity: Medium
Advisory: CVE-2026-54361
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:L/SI:L/SA:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-54361
Type: osv

## Details
MISP contained multiple mass assignment vulnerabilities in the handling of collections, tag collections, event delegations, and shadow attributes. Several controller actions accepted user-supplied fields that should have remained server-controlled, including record identifiers and ownership-related fields such as id, org_id, orgc_id, and user_id.

An authenticated attacker with access to the affected endpoints could craft requests containing protected fields in order to alter object ownership, redirect an update to another record, overwrite existing event delegation requests, or modify shadow attribute proposals belonging to another organization. This could result in unauthorized modification of MISP objects and, depending on object visibility and sharing configuration, unauthorized access to or transfer of sensitive threat intelligence data.

The issue was fixed by explicitly pinning ownership and identity fields to their stored values during edit operations and by removing user-supplied primary keys from create-only save paths.

Affected components:

  *  CollectionsController::edit()
  *  EventDelegationsController::delegateEvent()
  *  ShadowAttributesController::edit()
  *  TagCollectionsController::edit()915
  *  TagCollectionsController::editWithTags()


Attack requirements:
The attacker must be authenticated and able to reach the affected MISP endpoints. No user interaction is required.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54361.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-54361
- https://github.com/MISP/MISP/commit/9341690e9b6dde7f0605edea5533e05ba7362e35
- https://github.com/misp/misp
