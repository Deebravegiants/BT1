# [M] NocoDB: Shared-base link access can invite arbitrary users as persistent base members

## Summary
Severity: Medium
Advisory: GHSA-chqv-vrj7-qffp
CVE: CVE-2026-46552
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-chqv-vrj7-qffp
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0

## Details
### Summary

Shared-base sessions were granted the same base-member capabilities as authenticated viewers. Using only the shared-base UUID (`xc-shared-base-id`), an attacker could enumerate base members and invite an arbitrary email into the base as a real member. The invited user could then redeem the invite via the normal signup flow and retain authenticated access even after the owner revoked the shared link.

### Details

Shared-base sessions were mapped to `ProjectRoles.VIEWER` in `packages/nocodb/src/strategies/base-view.strategy/base-view.strategy.ts`, and `packages/nocodb/src/utils/acl.ts` granted `baseUserList` and `userInvite` to that role. The shared frontend (`packages/nc-gui/composables/useApi/interceptors.ts`) deliberately removed auth headers in favour of the shared-base header, but the ACL middleware did not distinguish shared sessions from genuine viewers.

The end-to-end chain:

- `GET /api/v2/meta/bases/:baseId/users` returned the member list to shared-base callers (`@Acl('baseUserList')`).
- `POST /api/v2/meta/bases/:baseId/users` accepted an invite from shared-base callers (`@Acl('userInvite')`); `base-users.service.ts` inserted a real `nc_users_v2` row with `invite_token` and a `nc_base_users_v2` row for the target base, with `invited_by = null`.
- The invited account redeemed the invite through the normal signup path (`users.service.ts`), gaining a persistent JWT scoped to the base.
- Revoking the shared link did not affect the redeemed account.

### Impact

- Confidentiality: shared-base link exposes member email addresses.
- Integrity: shared-base link can mutate base ACL state by creating new members.
- Persistence: link-based access converts into durable authenticated access that survives revocation of the share.

### Credit

This issue was reported by [@0xmrma](https://github.com/0xmrma).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-chqv-vrj7-qffp
- https://nvd.nist.gov/vuln/detail/CVE-2026-46552
- https://github.com/nocodb/nocodb
