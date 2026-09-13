# [C] Grav through 2.0.11 Authentication Bypass via Flex Objects

## Summary
Severity: Critical
Advisory: CVE-2026-72831
Aliases: GHSA-pc8m-jxvh-vmrc
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-72831
Type: osv

## Details
The Flex Objects plugin (through 1.4.6, tested with Grav 2.0.11) contains an incorrect authorization vulnerability in its Flex Objects API. FlexApiController::update() checks only the general Flex directory permission and does not apply the additional target/field/super-admin checks enforced by the dedicated Users and Groups API controllers. An authenticated account with api.access, admin.login, and users.update permissions (but without api.users.write or admin.super) can use the generic /api/v1/flex-objects/user-accounts endpoint to change a super administrator's password, or the /api/v1/flex-objects/user-groups endpoint to grant its group admin.super, resulting in full site takeover. Fixed in Flex Objects 1.4.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72831.json
- https://github.com/getgrav/grav/security/advisories/GHSA-pc8m-jxvh-vmrc
- https://nvd.nist.gov/vuln/detail/CVE-2026-72831
- https://www.vulncheck.com/advisories/grav-through-authentication-bypass-via-flex-objects
- https://github.com/getgrav/grav-plugin-admin2/commit/a0bf26f7e5d7a98894b7cd2b8c5afe419b264e53
- https://github.com/getgrav/grav-plugin-api/commit/8071c10bc3a4743a4b8cf003dfb1644d6680c2ea
- https://github.com/getgrav/grav/commit/ad9709f865b09b68798fb1ac375b484a8cc1d892
- https://github.com/trilbymedia/grav-plugin-flex-objects/commit/0b384f5b0e73b1ad9dd29c70185407895ea3b09f
