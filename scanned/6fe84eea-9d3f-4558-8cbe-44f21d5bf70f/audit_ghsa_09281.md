# [M] Nitro has an Open Redirect via Protocol-Relative URL Bypass in Wildcard Route Rules

## Summary
Severity: Medium
Advisory: GHSA-9phm-9p8f-hw5m
CVE: CVE-2026-44372
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-9phm-9p8f-hw5m
Type: github-advisory

## Affected
- npm: `nitro` — affected >=0 <3.0.260429-beta
- npm: `nitropack` — affected >=0 <2.13.4

## Details
A redirect route rule like:

```ts
routeRules: {
  "/legacy/**": { redirect: "/**" }
}
```

is intended to rewrite paths within the same host. Before the patch, an attacker could turn the rewrite into a cross-host redirect by sliding an extra slash in after the rule prefix. Example exploit:

```
GET /legacy//evil.com
```

Nitro stripped `/legacy` from the matched pathname and joined the remainder against the rule's target. The remainder was `//evil.com`, which the join preserved verbatim, so Nitro responded with `Location: //evil.com`. Browsers resolve `//evil.com` as a protocol-relative URL against the current scheme, sending the user to `https://evil.com`. 

### Are you affected?

Users may be affected if **all** of the following are true:

1. Their project uses Nitro's `routeRules` with a `redirect` entry.
2. The target uses a `/**` wildcard suffix to forward sub-paths (e.g. `redirect: "/**"`, `redirect: "/new/**"`, `proxy: { to: "http://upstream/**" }`).
3. The `redirect` rule is _not_ handled natively at the CDN layer. The `vercel`, `netlify`, `cloudflare-pages`, and `edgeone` presets translate `routeRules.redirect` into platform config (`vercel.json`, `_redirects`, EdgeOne v3 config) and serve the redirect at the edge — those deployments bypass the Nitro runtime entirely and are not affected. Every other preset executes the redirect through the Nitro runtime and can be vulnerable.

## Impact

Open redirect from any host serving Nitro with a wildcard `redirect` rule. The redirect target is fully attacker-controlled, the URL looks legitimate (it starts with the victim's domain), and the browser silently follows it.

## Patched versions

Upgrade to one of:

- [2.13.4](https://github.com/nitrojs/nitro/releases/tag/v2.13.4) or later (or upgrade lockfile with latest ufo 1.6.4+)
- [3.0.260429-beta](https://github.com/nitrojs/nitro/releases/tag/v3.0.260429-beta) or later (https://github.com/nitrojs/nitro/pull/4236)

The fix has two parts:

1. `ufo` is bumped to `^1.6.4` ([unjs/ufo@5cd9e67](https://github.com/unjs/ufo/commit/5cd9e676711af3f4e4b5398ddf6ca8d52c1c7e1f)), which collapses any run of leading slashes to a single `/` inside `withoutBase`. This covers the typical `"/scope/**"` rule.
2. The Nitro runtime additionally collapses leading `//` before joining when the rule path itself is `/**` (in rare case which case `withoutBase` is never called and the raw pathname flows straight into `joinURL("", …)`).

## References
- https://github.com/nitrojs/nitro/security/advisories/GHSA-9phm-9p8f-hw5m
- https://nvd.nist.gov/vuln/detail/CVE-2026-44372
- https://github.com/nitrojs/nitro/pull/4236
- https://github.com/unjs/ufo/commit/5cd9e676711af3f4e4b5398ddf6ca8d52c1c7e1f
- https://github.com/nitrojs/nitro
- https://github.com/nitrojs/nitro/releases/tag/v2.13.4
- https://github.com/nitrojs/nitro/releases/tag/v3.0.260429-beta
