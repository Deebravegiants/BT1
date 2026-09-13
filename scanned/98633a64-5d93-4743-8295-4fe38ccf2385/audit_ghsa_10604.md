# [C] @delmaredigital/payload-puc is missing authorization on /api/puck/* CRUD endpoints allows unauthenticated access to Puck-registered collections

## Summary
Severity: Critical
Advisory: GHSA-65w6-pf7x-5g85
CVE: CVE-2026-39397
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-65w6-pf7x-5g85
Type: github-advisory

## Affected
- npm: `@delmaredigital/payload-puck` — affected >=0 <0.6.23

## Details
### Impact

All `/api/puck/*` CRUD endpoint handlers registered by `createPuckPlugin()` called Payload's local API with the default `overrideAccess: true`, bypassing all collection-level access control. The `access` option passed to `createPuckPlugin()` and any `access` rules defined on Puck-registered collections were silently ignored on these endpoints.

An unauthenticated remote attacker could:

- List all documents (including drafts) in any Puck-registered collection
- Read any document by ID (including drafts)
- Create new documents with arbitrary field values
- Update any document (including bypassing field-level access rules)
- Delete any document
- Read version history and restore arbitrary versions

**In typical installations**, the affected scope is the collection backing the website's pages (default slug: `pages`). For most users this means an attacker could read, modify, create, or delete every page on the website — including unpublished drafts and version history.

**Scope is limited to collections explicitly registered with `createPuckPlugin()`** — the endpoints validate the collection slug against an allowlist, so attackers cannot pivot to other Payload collections such as `users`, `media`, or business data not exposed to the plugin. The auto-created `puck-templates`, `puck-ai-prompts`, and `puck-ai-context` collections are also outside the allowlist; they have their own dedicated endpoints with separate authentication.

Other endpoints in the plugin (AI, styles, prompts, context, and the Next.js API route factories in `src/api/`) were unaffected — they had their own authentication checks.

### Patches

Fixed in **0.6.23**. All endpoint handlers in `src/endpoints/index.ts` now pass `overrideAccess: false` and forward `req` to Payload's local API, so collection-level access rules are evaluated against the current user.

### Workarounds

If you cannot upgrade immediately, place a reverse-proxy or middleware authentication check in front of `/api/puck/*` to require an authenticated session before requests reach the plugin's handlers.

## References
- https://github.com/delmaredigital/payload-puck/security/advisories/GHSA-65w6-pf7x-5g85
- https://nvd.nist.gov/vuln/detail/CVE-2026-39397
- https://github.com/delmaredigital/payload-puck/issues/7
- https://github.com/delmaredigital/payload-puck/commit/9148201c6bbfa140d44546438027a2f8a70f79a4
- https://github.com/delmaredigital/payload-puck
