# [H] electron-updater: Cross-origin redirect leaks `PRIVATE-TOKEN` and mixed-case `Authorization` credentials in `builder-util-runtime`

## Summary
Severity: High
Advisory: GHSA-p2f4-r6v6-j797
CVE: CVE-2026-54673
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-p2f4-r6v6-j797
Type: github-advisory

## Affected
- npm: `builder-util-runtime` — affected >=0 <9.7.0

## Details
## Summary

In `electron-builder`'s `builder-util-runtime` package, the HTTP redirect handler (`HttpExecutor.prepareRedirectUrlOptions`) only stripped a credential header whose key string matched exactly lowercase `"authorization"`. Other credential-bearing headers — most notably `PRIVATE-TOKEN` (used by GitLab's personal access token flow) and mixed-case `Authorization` (used by GitLab's Bearer/OAuth flow) — were not stripped and could be forwarded to an attacker-controlled cross-origin redirect destination.

---

## Details

### Root cause

`HttpExecutor.prepareRedirectUrlOptions` (introduced in `builder-util-runtime` via [PR #9211](https://github.com/electron-userland/electron-builder/pull/9211), first released in `v26.0.20`) performed its cross-origin credential strip with a single case-sensitive property check:

```typescript
// vulnerable code (electron-builder v26.0.20 – v26.14.x) [via builder-util-runtime <9.7.0]
if (headers?.authorization) {
  if (HttpExecutor.isCrossOriginRedirect(originalUrl, parsedRedirectUrl)) {
    delete headers.authorization   // only removes the exact key "authorization"
  }
}
```

JavaScript object property access is case-sensitive. The guard `headers?.authorization` evaluates to `undefined` (falsy) when the key is `"Authorization"`, `"AUTHORIZATION"`, or any other casing, so the branch is never entered and **no header is deleted** for those cases.

### Affected updater flows

The clearest reproduced path is the private GitLab updater flow.

`packages/electron-updater/src/providers/GitLabProvider.ts` sets one of two credential headers depending on the token type:

```typescript
// GitLabProvider.setAuthHeaderForToken (affected versions)
if (token.startsWith("Bearer")) {
  headers.authorization = token        // Bearer / OAuth token  →  key is lowercase
} else {
  headers["PRIVATE-TOKEN"] = token     // personal access token →  key is "PRIVATE-TOKEN"
}
```

During a private release update check, the updater requests a release asset through GitLab's `direct_asset_url`. GitLab commonly redirects asset downloads to an external object-storage origin (e.g., S3, GCS). Because the redirect crosses origins:

1. A personal access token in `PRIVATE-TOKEN` **is never inspected** by the vulnerable strip guard — it is forwarded intact.
2. A Bearer token set as `headers.authorization` (lowercase) **is stripped** correctly.
3. A Bearer token set as `headers.Authorization` (capital A) or any other mixed-case variant **bypasses the guard** and is forwarded intact.

GitLab is the concrete reproduced case; any other provider or custom updater configuration that places credentials in a non-lowercase-`authorization` header is equally affected.

### Before v26.0.20

Versions prior to `v26.0.20` did not contain `prepareRedirectUrlOptions` at all. All credential headers were forwarded unchanged on every redirect, regardless of origin. This represents a broader, pre-existing version of the same class of vulnerability.

---

## Proof of concept (reproduction shape)

1. Configure the updater with an authenticated GitLab provider, supplying a personal access token (non-Bearer). The provider will set `PRIVATE-TOKEN: <token>` on requests.
2. Trigger an update check. The updater fetches release metadata and then requests a release asset URL.
3. The trusted GitLab origin returns a 3xx cross-origin redirect (e.g., to S3 object storage).
4. `HttpExecutor.prepareRedirectUrlOptions` is called. The guard `headers?.authorization` is falsy (the key is `"PRIVATE-TOKEN"`). No header is deleted.
5. The request to the redirect destination is issued with `PRIVATE-TOKEN: <token>` present in the headers.

**Observed result:** The personal access token is forwarded to the redirect destination. An attacker who controls or can observe the redirect destination receives the token.

---

## Impact

This is a credential disclosure vulnerability. An automatic update check can leak:

- GitLab personal access tokens (`PRIVATE-TOKEN`)
- Bearer/OAuth tokens sent under a mixed-case `Authorization` key
- Any other credential header not named exactly `"authorization"` in lowercase

Disclosure of a GitLab PAT grants the attacker whatever repository and API permissions the token carries, enabling unauthorized access to private source code, packages, or release artifacts.

---

## Patches

Fixed in electron-builder `v26.15.0` [included via `v9.7.0` `builder-util-runtime`] via [PR #9834](https://github.com/electron-userland/electron-builder/pull/9834) (commit [`22a7532bd`](https://github.com/electron-userland/electron-builder/commit/22a7532bd01b9fb42cff7c58d599c7ad683569fe)).

The incomplete property-access guard was replaced with a separator-agnostic, case-insensitive lookup against a registry of known sensitive header names:

```typescript
// fixed code (v9.7.0+)
const normalizeName = (name: string): string =>
  name.toLowerCase().replace(/[-_]/g, "")

const SENSITIVE_REDIRECT_HEADERS = new Set([
  "authorization", "proxyauthorization", "privatetoken",
  "xapikey", "xauthtoken", "xaccesstoken", "xgitlabtoken",
  "cookie", "xcsrftoken",
])

// In prepareRedirectUrlOptions, on cross-origin redirect:
for (const key of Object.keys(headers)) {
  if (SENSITIVE_REDIRECT_HEADERS.has(normalizeName(key))) {
    delete (headers as Record<string, unknown>)[key]
  }
}
```

`normalizeName` converts to lowercase and strips `-` and `_` separators, so `PRIVATE-TOKEN`, `Private-Token`, `Authorization`, `AUTHORIZATION`, `X-Api-Key`, etc. are all matched. The fix also exports `addSensitiveRedirectHeader()` to allow custom publishers to register additional headers.

**Upgrade path:** Update `builder-util-runtime` to `>= 9.7.0`.

---

## Workarounds

There is no configuration-level workaround that prevents header forwarding in affected versions. The only mitigation short of upgrading is to avoid authenticated GitLab updater flows on versions `< 9.7.0`.

If operating in a network environment where you control all possible redirect destinations, you may be able to prevent the token from reaching an attacker-controlled host through network-layer controls, but this is not a reliable mitigation.

## References
- https://github.com/electron-userland/electron-builder/security/advisories/GHSA-p2f4-r6v6-j797
- https://nvd.nist.gov/vuln/detail/CVE-2026-54673
- https://github.com/electron-userland/electron-builder/pull/9834
- https://github.com/electron-userland/electron-builder/commit/22a7532bd01b9fb42cff7c58d599c7ad683569fe
- https://github.com/electron-userland/electron-builder
- https://github.com/electron-userland/electron-builder/releases/tag/electron-builder@26.15.0
