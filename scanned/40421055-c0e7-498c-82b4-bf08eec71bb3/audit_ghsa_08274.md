# [C] Malware in @tanstack/* packages exfiltrates cloud credentials, GitHub tokens, and SSH keys

## Summary
Severity: Critical
Advisory: GHSA-g7cv-rxg3-hmpx
CVE: CVE-2026-45321
CWE: CWE-506
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-g7cv-rxg3-hmpx
Type: github-advisory

## Affected
- npm: `@tanstack/arktype-adapter` — affected >=1.166.12 <1.166.16
- npm: `@tanstack/eslint-plugin-router` — affected >=1.161.9 <1.161.13
- npm: `@tanstack/eslint-plugin-start` — affected >=0.0.4 <0.0.8
- npm: `@tanstack/history` — affected >=1.161.9 <1.161.13
- npm: `@tanstack/nitro-v2-vite-plugin` — affected >=1.154.12 <1.154.16
- npm: `@tanstack/react-router` — affected >=1.169.5 <1.169.9
- npm: `@tanstack/react-router-devtools` — affected >=1.166.16 <1.166.20
- npm: `@tanstack/react-router-ssr-query` — affected >=1.166.15 <1.166.19
- npm: `@tanstack/react-start` — affected >=1.167.68 <1.167.72
- npm: `@tanstack/react-start-client` — affected >=1.166.51 <1.166.55
- npm: `@tanstack/react-start-rsc` — affected >=0.0.47 <0.0.51
- npm: `@tanstack/react-start-server` — affected >=1.166.55 <1.166.59
- npm: `@tanstack/router-cli` — affected >=1.166.46 <1.166.50
- npm: `@tanstack/router-core` — affected >=1.169.5 <1.169.9
- npm: `@tanstack/router-devtools` — affected >=1.166.16 <1.166.20
- npm: `@tanstack/router-devtools-core` — affected >=1.167.6 <1.167.10
- npm: `@tanstack/router-generator` — affected >=1.166.45 <1.166.49
- npm: `@tanstack/router-plugin` — affected >=1.167.38 <1.167.42
- npm: `@tanstack/router-ssr-query-core` — affected >=1.168.3 <1.168.7
- npm: `@tanstack/router-utils` — affected >=1.161.11 <1.161.15
- npm: `@tanstack/router-vite-plugin` — affected >=1.166.53 <1.166.57
- npm: `@tanstack/solid-router` — affected >=1.169.5 <1.169.9
- npm: `@tanstack/solid-router-devtools` — affected >=1.166.16 <1.166.20
- npm: `@tanstack/solid-router-ssr-query` — affected >=1.166.15 <1.166.19
- npm: `@tanstack/solid-start` — affected >=1.167.65 <1.167.69
- npm: `@tanstack/solid-start-client` — affected >=1.166.50 <1.166.54
- npm: `@tanstack/solid-start-server` — affected >=1.166.54 <1.166.58
- npm: `@tanstack/start-client-core` — affected >=1.168.5 <1.168.9
- npm: `@tanstack/start-fn-stubs` — affected >=1.161.9 <1.161.13
- npm: `@tanstack/start-plugin-core` — affected >=1.169.23 <1.169.27
- npm: `@tanstack/start-server-core` — affected >=1.167.33 <1.167.37
- npm: `@tanstack/start-static-server-functions` — affected >=1.166.44 <1.166.48
- npm: `@tanstack/start-storage-context` — affected >=1.166.38 <1.166.42
- npm: `@tanstack/valibot-adapter` — affected >=1.166.12 <1.166.16
- npm: `@tanstack/virtual-file-routes` — affected >=1.161.10 <1.161.14
- npm: `@tanstack/vue-router` — affected >=1.169.5 <1.169.9
- npm: `@tanstack/vue-router-devtools` — affected >=1.166.16 <1.166.20
- npm: `@tanstack/vue-router-ssr-query` — affected >=1.166.15 <1.166.19
- npm: `@tanstack/vue-start` — affected >=1.167.61 <1.167.65
- npm: `@tanstack/vue-start-client` — affected >=1.166.46 <1.166.50
- npm: `@tanstack/vue-start-server` — affected >=1.166.50 <1.166.54
- npm: `@tanstack/zod-adapter` — affected >=1.166.12 <1.166.16
- npm: `@tanstack/arktype-adapter` — affected >=1.166.15 <1.166.16
- npm: `@tanstack/eslint-plugin-router` — affected >=1.161.12 <1.161.13
- npm: `@tanstack/eslint-plugin-start` — affected >=0.0.7 <0.0.8
- npm: `@tanstack/history` — affected >=1.161.12 <1.161.13
- npm: `@tanstack/nitro-v2-vite-plugin` — affected >=1.154.15 <1.154.16
- npm: `@tanstack/react-router` — affected >=1.169.8 <1.169.9
- npm: `@tanstack/react-router-devtools` — affected >=1.166.19 <1.166.20
- npm: `@tanstack/react-router-ssr-query` — affected >=1.166.18 <1.166.19
- npm: `@tanstack/react-start` — affected >=1.167.71 <1.167.72
- npm: `@tanstack/react-start-client` — affected >=1.166.54 <1.166.55
- npm: `@tanstack/react-start-rsc` — affected >=0.0.50 <0.0.51
- npm: `@tanstack/react-start-server` — affected >=1.166.58 <1.166.59
- npm: `@tanstack/router-cli` — affected >=1.166.49 <1.166.50
- npm: `@tanstack/router-core` — affected >=1.169.8 <1.169.9
- npm: `@tanstack/router-devtools` — affected >=1.166.19 <1.166.20
- npm: `@tanstack/router-devtools-core` — affected >=1.167.9 <1.167.10
- npm: `@tanstack/router-generator` — affected >=1.166.48 <1.166.49
- npm: `@tanstack/router-plugin` — affected >=1.167.41 <1.167.42
- npm: `@tanstack/router-ssr-query-core` — affected >=1.168.6 <1.168.7
- npm: `@tanstack/router-utils` — affected >=1.161.14 <1.161.15
- npm: `@tanstack/router-vite-plugin` — affected >=1.166.56 <1.166.57
- npm: `@tanstack/solid-router` — affected >=1.169.8 <1.169.9
- npm: `@tanstack/solid-router-devtools` — affected >=1.166.19 <1.166.20
- npm: `@tanstack/solid-router-ssr-query` — affected >=1.166.18 <1.166.19
- npm: `@tanstack/solid-start` — affected >=1.167.68 <1.167.69
- npm: `@tanstack/solid-start-client` — affected >=1.166.53 <1.166.54
- npm: `@tanstack/solid-start-server` — affected >=1.166.57 <1.166.58
- npm: `@tanstack/start-client-core` — affected >=1.168.8 <1.168.9
- npm: `@tanstack/start-fn-stubs` — affected >=1.161.12 <1.161.13
- npm: `@tanstack/start-plugin-core` — affected >=1.169.26 <1.169.27
- npm: `@tanstack/start-server-core` — affected >=1.167.36 <1.167.37
- npm: `@tanstack/start-static-server-functions` — affected >=1.166.47 <1.166.48
- npm: `@tanstack/start-storage-context` — affected >=1.166.41 <1.166.42
- npm: `@tanstack/valibot-adapter` — affected >=1.166.15 <1.166.16
- npm: `@tanstack/virtual-file-routes` — affected >=1.161.13 <1.161.14
- npm: `@tanstack/vue-router` — affected >=1.169.8 <1.169.9
- npm: `@tanstack/vue-router-devtools` — affected >=1.166.19 <1.166.20
- npm: `@tanstack/vue-router-ssr-query` — affected >=1.166.18 <1.166.19
- npm: `@tanstack/vue-start` — affected >=1.167.64 <1.167.65
- npm: `@tanstack/vue-start-client` — affected >=1.166.49 <1.166.50
- npm: `@tanstack/vue-start-server` — affected >=1.166.53 <1.166.54
- npm: `@tanstack/zod-adapter` — affected >=1.166.15 <1.166.16

## Details
## Summary

On 2026-05-11, between approximately 19:20 and 19:26 UTC, 84 malicious versions across 42 `@tanstack/*` packages were published to the npm registry. The publishes were authenticated via the legitimate GitHub Actions OIDC trusted-publisher binding for `TanStack/router`, but the publish workflow itself was not modified. The attacker chained three known vulnerability classes — a `pull_request_target` "Pwn Request" misconfiguration, GitHub Actions cache poisoning across the fork↔base trust boundary, and runtime memory extraction of the OIDC token from the Actions runner process — to publish credential-stealing malware under a trusted identity.

Each affected package received exactly two malicious versions, published a few minutes apart.

## Impact

A user installing any affected version executes a payload (~2.3 MB obfuscated `router_init.js`) at install time that:

- Harvests credentials from common locations:
  - AWS instance metadata (IMDS) and Secrets Manager
  - GCP metadata service
  - Kubernetes service-account tokens
  - HashiCorp Vault tokens
  - `~/.npmrc` (npm tokens)
  - GitHub tokens (env vars, `gh` CLI config, `.git-credentials`)
  - SSH private keys (`~/.ssh/`)
- Exfiltrates harvested data over the Session/Oxen messenger file-upload network (`filev2.getsession.org`, `seed{1,2,3}.getsession.org`). This is end-to-end encrypted with no attacker-controlled C2, so blocking by IP or domain is the only network mitigation.
- Enumerates packages that the victim maintains via `registry.npmjs.org/-/v1/search?text=maintainer:<user>` and republishes them with the same injection, propagating the compromise across npm.

Any developer or CI environment that ran `npm install`, `pnpm install`, or `yarn install` against an affected version on 2026-05-11 should be considered compromised. All credentials accessible to the install process should be rotated immediately. Cloud audit logs should be reviewed for activity originating from the affected hosts during and after the install window.

## Detection

Inspect the published manifest of any pinned `@tanstack/*` version. Malicious manifests contain this exact `optionalDependencies` entry:

```json
"optionalDependencies": {
  "@tanstack/setup": "github:tanstack/router#79ac49eedf774dd4b0cfa308722bc463cfe5885c"
}
```

To check a version without running install scripts:

```bash
npm pack @tanstack/<name>@<version>   # downloads tarball; does NOT execute lifecycle scripts
tar -xzf *.tgz
grep -A3 optionalDependencies package/package.json
ls -la package/router_init.js   # malicious payload, ~2.3 MB, present at package root
```

The payload file `router_init.js` is approximately 2.3 MB of obfuscated JavaScript. It is placed at the tarball root and is intentionally not declared in the package's `"files"` array, so it does not appear in the package's documented contents.

## Mechanism

`@tanstack/setup` is not a real package on the npm registry. The `github:tanstack/router#79ac49ee...` specifier resolves to an orphan commit pushed to a fork in the `tanstack/router` GitHub fork network. GitHub serves commits across the entire fork network for git-URL dependencies, so the attacker did not require write access to `TanStack/router` itself — only the ability to fork and push to their own fork.

When npm processes the optional dependency, it:

1. Fetches the orphan commit from the fork network.
2. Installs the commit's declared dependencies (which include a real `bun` binary).
3. Runs the commit's `prepare` lifecycle script: `bun run tanstack_runner.js && exit 1`. The trailing `exit 1` causes the optional install to fail, after which npm silently discards it — leaving no `node_modules` trace.
4. The `tanstack_runner.js` script in turn executes `router_init.js` from the host package's tarball.

## Patches

Affected versions are being deprecated on npm with a `SECURITY:` notice. Where npm policy allows (no existing third-party dependents), affected versions are also being unpublished. The npm security team has been engaged to pull tarballs server-side for versions that cannot be unpublished.

Clean follow-up releases are being prepared. Update to the patched version listed in the affected-products table for each package, then reinstall from a clean lockfile.

## Workarounds

Until clean follow-up releases are available:

- Pin every `@tanstack/*` dependency to a known-good version published before 2026-05-11 19:00 UTC. The last known-good version for most affected packages was published on 2026-03-15.
- Delete `node_modules` and the lockfile, then reinstall to ensure no transitive dependency resolves to a malicious version.
- Configure npm to skip lifecycle scripts on install (`npm config set ignore-scripts true`) as a temporary defense-in-depth measure.
- For CI, audit any pipeline that ran `install` against `@tanstack/*` between 19:20 and 19:30 UTC on 2026-05-11. Treat the runner as compromised and rotate any secrets it had access to.

## Indicators of compromise

| Indicator | Value |
|---|---|
| Malicious git ref | `github:tanstack/router#79ac49eedf774dd4b0cfa308722bc463cfe5885c` |
| Fictitious package name | `@tanstack/setup` |
| Payload filename | `router_init.js` (~2.3 MB, package root, undeclared in `files`) |
| Helper filename in orphan commit | `tanstack_runner.js` |
| Exfiltration network | `filev2.getsession.org`, `seed1.getsession.org`, `seed2.getsession.org`, `seed3.getsession.org` |
| Second-stage payload URLs | `https://litter.catbox.moe/h8nc9u.js`, `https://litter.catbox.moe/7rrc6l.mjs` |
| Poisoned cache key | `Linux-pnpm-store-6f9233a50def742c09fde54f56553d6b449a535adf87d4083690539f49ae4da11` |
| Publish window (UTC) | 2026-05-11 19:20 — 19:26 |
| Publish mechanism | GitHub Actions OIDC trusted publisher (`oidc:db7d6f54-05d5-412b-8a10-e7a8398b303e`) |
| Workflow runs | https://github.com/TanStack/router/actions/runs/25613093674 (attempt 4), https://github.com/TanStack/router/actions/runs/25691781302 |
| Attacker GitHub accounts | `zblgg` (id 127806521), `voicproducoes` (id 269549300) |
| Attacker fork (renamed to evade detection) | https://github.com/zblgg/configuration |

## Credits

- The security researcher who initially disclosed the vulnerability publicly with detailed analysis at https://github.com/TanStack/router/issues/7383

## References

- Public incident tracking issue: https://github.com/TanStack/router/issues/7383
- Related research:
  - Adnan Khan, "The Monsters in Your Build Cache: GitHub Actions Cache Poisoning" (May 2024)
  - GitHub Security Lab, "Keeping your GitHub Actions and workflows secure: Preventing Pwn Requests"
  - StepSecurity, "tj-actions/changed-files action is compromised" (March 2025) — the malicious payload reuses this incident's runner-memory extraction technique verbatim

## References
- https://github.com/TanStack/router/security/advisories/GHSA-g7cv-rxg3-hmpx
- https://nvd.nist.gov/vuln/detail/CVE-2026-45321
- https://github.com/TanStack/router/issues/7383
- https://github.com/TanStack/router
- https://socket.dev/blog/tanstack-npm-packages-compromised-mini-shai-hulud-supply-chain-attack
- https://tanstack.com/blog/npm-supply-chain-compromise-postmortem
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-45321
- https://www.stepsecurity.io/blog/mini-shai-hulud-is-back-a-self-spreading-supply-chain-attack-hits-the-npm-ecosystem
