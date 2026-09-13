# [M] Windmill: Resource-scoped API tokens can read script contents outside their allowed path via scripts/list_search

## Summary
Severity: Medium
Advisory: GHSA-2ppx-66jv-wpw5
CVE: CVE-2026-54136
CWE: CWE-863
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-2ppx-66jv-wpw5
Type: github-advisory

## Affected
- crates.io: `windmill-api` — affected >=0 <1.715.0

## Details
### Summary

A resource-scoped API token can read script contents outside its allowed path scope via `GET /api/w/{workspace}/scripts/list_search`.

This appears to be a remaining variant of the scoped-token authorization class previously addressed for other endpoints. The route-level scope middleware validates the token domain/action, but does not enforce the resource/path segment of a scope. `scripts/list_search` then returns script `path` and `content` for scripts in the workspace without applying per-row path filtering against the token scopes.

### Affected endpoint

`GET /api/w/{workspace}/scripts/list_search`

### Affected versions

Confirmed in the current public repository code and believed to affect the latest published release at the time of review:

`<= 1.714.1`

Patched version: unknown.

### Details

Windmill supports scoped API tokens with scopes in the format:

`{domain}:{action}[:{resource}]`

The parser supports resource-scoped values such as:

`scripts:read:f/allowed/*`

and the codebase contains helpers for resource matching, including wildcard matching.

However, the route-level scope check used for requests with scoped API tokens only validates the route domain and action. It does not compare the token's resource/path restriction against the requested route or against the rows returned by list endpoints.

For `scripts/list_search`, the handler returns `path` and `content` for scripts in the workspace:

`SELECT path, content from script WHERE workspace_id = $1 AND archived = false LIMIT $2`

There is no additional `check_scopes(...)` call in the handler and no per-row filtering based on the token's resource/path scope.

As a result, a token intended to read only scripts under one path prefix may be able to read script contents from unrelated paths in the same workspace.

### Source-level reproduction

1. Create or use a workspace containing at least two scripts:

- `f/allowed/script_a`
- `f/private/script_b`

2. Create a scoped API token intended to read only the allowed path:

`scripts:read:f/allowed/*`

3. Use that token to call:

`GET /api/w/{workspace}/scripts/list_search`

4. Expected behavior:

The response should include only scripts matching the token's resource scope, e.g. only scripts under:

`f/allowed/*`

5. Actual behavior from source review:

The route-level scope check accepts the request as `scripts:read`, and the handler returns script `path` and `content` for scripts in the workspace without filtering the rows by the token's resource scope.

This can expose script source code from paths outside the token's intended scope.

### Impact

A user or integration holding a path-restricted `scripts:read:{resource}` token may be able to read script contents from unrelated scripts in the same workspace.

Depending on how scripts are used, this may disclose:

- internal automation logic,
- integration details,
- business logic,
- inline configuration,
- accidentally hardcoded secrets or credentials.

This does not require admin privileges. It requires possession of a valid scoped API token for the workspace.

### Related context

This appears related to the broader class of issues where route-level token scope enforcement validates domain/action but not the resource/path portion of the scope. Similar scoped-token issues appear to have been fixed for other endpoints, such as resources/variables listing and job preview/run paths, but I did not find an equivalent fix for `scripts/list_search`.

### Suggested fix

Apply resource/path scope enforcement to `scripts/list_search`.

Possible approaches:

1. Add explicit handler-level authorization similar to per-resource endpoints.
2. Filter returned rows so that a scoped token only receives scripts whose `path` is included by at least one `scripts:read:{resource}` scope.
3. Add regression tests for:
   - `scripts:read:f/allowed/*` cannot see `f/private/script_b`,
   - broad `scripts:read` still sees all accessible scripts,
   - unscoped tokens preserve current behavior,
   - filter-tag-only tokens preserve current compatibility behavior.

A more defensive long-term fix would be to make route-level scope enforcement aware of resource/path restrictions where the route contains a concrete resource path, while list endpoints should apply per-row filtering.

## References
- https://github.com/windmill-labs/windmill/security/advisories/GHSA-2ppx-66jv-wpw5
- https://github.com/windmill-labs/windmill
