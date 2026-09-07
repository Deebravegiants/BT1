# [H] @better-auth/sso: SSO provider may allow registration for any org member without a checking their role

## Summary
Severity: High
Advisory: GHSA-gv74-j8m3-fg5f
CVE: CVE-2026-53515
CWE: CWE-269, CWE-285, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-gv74-j8m3-fg5f
Type: github-advisory

## Affected
- npm: `@better-auth/sso` — affected >=1.2.10 <1.6.11

## Details
### Am I affected?

You are affected if all of the following are true:

- You depend on `@better-auth/sso` at any version in `>= 1.2.10, < 1.6.11`, or any current `next` pre-release.
- You enable both `sso()` and `organization()` plugins.
- `providersLimit` is at its default (`10`) or any non-zero value, so SSO provider registration is enabled for authenticated users.
- An organization has non-admin members, or your application can add users to organizations as regular members.

You are at the highest risk if any of these also hold:

- Organization membership can be obtained without a direct admin decision, such as through open invitations, self-serve onboarding, public team joins, or SCIM bulk imports.
- `organizationProvisioning.defaultRole` or `organizationProvisioning.getRole` returns `admin` or higher for SSO-provisioned users. The bug then becomes unauthorized admin creation in the org.
- `domainVerification.enabled` is `false` (the default). The malicious provider is immediately usable.

Fix:

1. Upgrade to `@better-auth/sso@1.6.11` or later.
2. If you cannot upgrade, see workarounds below.

### Summary

The SSO plugin's `POST /sso/register` endpoint lets any member of an organization attach a new SSO provider to that organization. It checks that the caller has a membership row, but it does not check whether the caller has an administrative role for the organization.

This creates an authorization mismatch for the same resource. Other org-linked SSO provider management endpoints treat those providers as admin-managed: list, get, update, and delete require the caller to be an organization `owner` or `admin`. The create path is less restrictive, so a regular member can attach an attacker-controlled OIDC or SAML identity provider to an organization they do not administer. After registration, downstream organization provisioning can add IdP-asserted users from `/sso/callback/{providerId}` into the target organization, defaulting to role `member`.

### Details

This issue does not rely on a separate documentation statement that only admins may create SSO connections. The issue is that Better Auth already enforces an admin boundary for org-linked SSO provider management, but `registerSSOProvider` does not enforce the same boundary when the provider is first created.

The list, get, update, and delete endpoints in `providers.ts` gate org-linked SSO providers via `isOrgAdmin`, which accepts `owner` or `admin`. The create path in `sso.ts` performs only a membership lookup and never inspects `member.role`. As a result, the endpoint allows a low-privilege organization member to create a provider record that they would not be allowed to view, update, or delete through the companion provider-management endpoints.

The fix introduces a shared `hasOrgAdminRole(member)` helper (refactored out of `isOrgAdmin`) and adds the admin check to the registration handler so that registration matches the protections on the read and mutation paths.

### Patches

Fixed in `@better-auth/sso@1.6.11`. When `organizationId` is supplied and the `organization` plugin is enabled, the `registerSSOProvider` handler now requires the caller to hold the `owner` or `admin` role on the target organization. This makes provider creation match the existing protection on the get, update, and delete endpoints.

### Workarounds

If you cannot upgrade immediately:

- **Disable user-driven SSO registration entirely**: set `sso({ providersLimit: 0 })`. Registration throws `FORBIDDEN` before the membership gate. Trade-off: admins also lose self-serve provider creation; provisioning has to go through server-side `auth.api.registerSSOProvider({ headers: serverAdminHeaders, body })` calls.
- **Disable SSO-driven org provisioning**: set `sso({ organizationProvisioning: { disabled: true } })`. The malicious provider can still be registered, but the SSO callback no longer adds users to the org automatically. Trade-off: legitimate SSO-driven onboarding stops.
- **Custom `before` hook on `/sso/register`** that asserts the caller's role on `body.organizationId` is `owner` or `admin`. This duplicates the patch shape in user code.
- **Audit existing rows**: list `ssoProvider` rows where `organizationId IS NOT NULL`, cross-reference each `userId` with `member.role` for that organization, and remove provider rows whose creator is not currently `owner` or `admin`. Removing the provider does not auto-remove members it created, so cleanup is two-step.

### Impact

- **Unauthorized provider configuration within an organization tenant**: a regular member writes an SSO provider record on an organization they do not administer.
- **Unauthorized organization membership creation**: subsequent SSO callbacks can add IdP-asserted users to the target organization at the configured default role.
- **Admin creation when configured**: if `organizationProvisioning.defaultRole` is `admin`, or `organizationProvisioning.getRole` returns `admin`, the issue can create admin-grade users in the target organization without owner consent.

### Credit

Reported by @Nadav0077. The same finding was previously raised in public issue [#9133](https://github.com/better-auth/better-auth/issues/9133) (2026-04-12).

## References
- https://github.com/better-auth/better-auth/security/advisories/GHSA-gv74-j8m3-fg5f
- https://nvd.nist.gov/vuln/detail/CVE-2026-53515
- https://github.com/better-auth/better-auth/issues/9133
- https://github.com/better-auth/better-auth/pull/9220
- https://github.com/better-auth/better-auth/commit/86765f1597378f5c3deed1b80ca91faac0a6bf00
- https://github.com/better-auth/better-auth
- https://github.com/better-auth/better-auth/releases/tag/v1.6.11
