# [M] Onyx Curator-scope IDOR: any curator can modify membership of arbitrary user groups via unscoped PATCH /manage/admin/user-group/{id} and /add-users leading to cross-group document disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-63178
Aliases: GHSA-7f48-vgpj-h95m
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-63178
Type: osv

## Details
Onyx is an open-source AI platform. Prior to 4.3.0, Onyx Enterprise Edition's PATCH /manage/admin/user-group/{user_group_id} and POST /manage/admin/user-group/{user_group_id}/add-users endpoints in ee/onyx/server/user_group/api.py call update_user_group and add_users_to_user_group in ee/onyx/db/user_group.py without enforcing _validate_curator_can_modify_group, allowing a curator to add accounts to arbitrary groups and obtain document access through get_acl_for_user and the OpenSearch access_control_list filter. This issue is fixed in version 4.3.0.

## References
- https://github.com/onyx-dot-app/onyx/releases/tag/v4.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63178.json
- https://github.com/onyx-dot-app/onyx/security/advisories/GHSA-7f48-vgpj-h95m
- https://nvd.nist.gov/vuln/detail/CVE-2026-63178
- https://github.com/onyx-dot-app/onyx/commit/46e19cc2750fed659488cb12a1f171016ba5a099
- https://github.com/onyx-dot-app/onyx/commit/b9e1c6894be3c237283f4b5fd4eb0af935b40664
- https://github.com/onyx-dot-app/onyx/pull/12525
- https://github.com/onyx-dot-app/onyx/pull/12549
