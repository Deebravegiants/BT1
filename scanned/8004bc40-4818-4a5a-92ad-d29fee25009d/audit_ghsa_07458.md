# [H] @better-auth/stripe: cross-organization billing tampering in organization subscription actions

## Summary
Severity: High
Advisory: GHSA-h3rm-78g3-j7cp
CWE: CWE-639, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-h3rm-78g3-j7cp
Type: github-advisory

## Affected
- npm: `@better-auth/stripe` — affected >=1.4.11 <1.6.21
- npm: `@better-auth/stripe` — affected >=1.7.0-beta.0 <1.7.0-beta.10

## Details
### Am I affected?

You are affected if all of these are true:

- You use `@better-auth/stripe` from version 1.4.11 up to a patched version below. This covers the stable line through 1.6.20 and every 1.7.0 beta through 1.7.0-beta.9.
- The Stripe plugin has subscriptions turned on (`subscription.enabled: true`).
- Organization subscriptions are turned on (`organization.enabled: true`) and you have set an `authorizeReference` callback.
- A user can join more than one org. So a user can be a member of an org whose billing they should not manage.

You are not affected if you only use user subscriptions. You are also not affected if org subscriptions are turned off.

### Summary

An org subscription action can run against the wrong org. The actions are cancel, change plan, restore, and open the billing portal. The plugin checks permission against the org id in the request query string. It then runs the action against the caller's active org from their session. When these two ids differ, a member can act on billing for an org they may not manage. The target is always an org the caller belongs to.

### Details

The plugin runs two steps for each org subscription action. First, a middleware decides if the caller may use the requested org. It reads the org id from the request body or the query string. It then passes that id to your `authorizeReference` callback. Second, the route handler runs the action. The handler reads the org id from the request body only. It falls back to the active org in the session when the body has no id.

The gap is the query string. A caller puts an org they may manage in the query string. The middleware approves that org. The handler ignores the query string. It finds no id in the body, so it acts on the caller's active org instead. The check and the action no longer agree.

### Patches

Upgrade to one of these patched versions:

- Stable: `@better-auth/stripe@1.6.21` or later.
- Beta: `@better-auth/stripe@1.7.0-beta.10` or later.

The fix resolves the org id once in the middleware. It passes that single value to the handler. The approved org and the acted-on org are now always the same.

### Workarounds

If you cannot upgrade, make `authorizeReference` approve only the caller's active org. Return `false` when the requested id is not the active org id. Keep your existing role check too:

```ts
if (referenceId !== session.activeOrganizationId) {
  return false;
}
```

This forces the approved org and the active org to be the same value.

### Impact

- A signed-in member can make a subscription action run against the wrong org. The action can be cancel, change plan, restore, or billing portal. The target is limited to orgs the member belongs to.
- Through the billing portal, a member can reach another org's billing details. This includes payment methods, invoices, and subscription state.

### Credit

Reported and fixed by Taesu ([@bytaesu](https://github.com/bytaesu)).

## References
- https://github.com/better-auth/better-auth/security/advisories/GHSA-h3rm-78g3-j7cp
- https://github.com/better-auth/better-auth/commit/29fbcb573261242d8a05b131a9d39c9ae4352b06
- https://github.com/better-auth/better-auth
- https://github.com/better-auth/better-auth/releases/tag/v1.6.21
- https://github.com/better-auth/better-auth/releases/tag/v1.7.0-beta.10
