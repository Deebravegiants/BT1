# [C] Unauthenticated Nuxt DevTools RPC allows arbitrary command execution on the developer's host

## Summary
Severity: Critical
Advisory: GHSA-279x-mwfv-vcqv
CVE: CVE-2026-71319
CWE: CWE-306, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-279x-mwfv-vcqv
Type: github-advisory

## Affected
- npm: `@nuxt/devtools` — affected >=0 <3.3.1

## Details
### Impact

Nuxt DevTools (development mode only) exposes a bidirectional RPC channel over the Vite HMR WebSocket via the `nuxt:devtools:rpc` plugin. On affected versions the channel has no authentication: any client that can reach the Vite HMR endpoint (`ws://<host>:<port>/`, subprotocol `vite-hmr`) can call RPC methods, with no token, handshake, or origin check before the channel is established. The `updateOptions()`, `clearOptions()`, and `openInEditor()` methods do not enforce the `ensureDevAuthToken` check that the other mutating methods use.

`openInEditor()` reads the persisted `behavior.openInEditor` value and passes it to the `launch-editor` package, which spawns it as a child process. That value is settable through the equally unauthenticated `updateOptions()`. An attacker who can reach the HMR port can therefore chain `updateOptions('behavior', { openInEditor: '<command>' })` then `openInEditor('<any-existing-file>')` to execute an arbitrary program on the developer's machine.

The HMR port is reachable by a process on the same host, by any peer on the LAN when the dev server is bound with `nuxi dev --host`, or by a malicious website the developer visits while the dev server is running (a browser can open the HMR WebSocket cross-origin). Impact is limited to development environments; production builds do not run DevTools.

### Patches

Fixed in `@nuxt/devtools@3.3.1`. Because `nuxt` depends on `@nuxt/devtools` through a `^3.x` range, updating is a lockfile refresh / reinstall; no `nuxt` release is required.

### Workarounds

- Update `@nuxt/devtools` to a patched version.
- Do not run the dev server bound to a non-loopback interface (`nuxi dev --host`) on an untrusted network.
- Disable DevTools entirely with `devtools: { enabled: false }` in `nuxt.config`.

### References

- GHSA-279x-mwfv-vcqv
- `launch-editor`: https://www.npmjs.com/package/launch-editor

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-279x-mwfv-vcqv
- https://github.com/nuxt/nuxt
