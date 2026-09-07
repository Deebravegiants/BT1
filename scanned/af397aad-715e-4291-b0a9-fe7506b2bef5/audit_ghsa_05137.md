# [M] Nuxt dev server vite-node IPC socket is world-connectable on Linux

## Summary
Severity: Medium
Advisory: GHSA-534h-c3cw-v3h9
CWE: CWE-276
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-534h-c3cw-v3h9
Type: github-advisory

## Affected
- npm: `nuxt` — affected >=4.0.0 <4.4.7
- npm: `nuxt` — affected >=3.18.0 <3.21.7

## Details
### Impact

When running `nuxt dev` on Linux (Node.js 20+, outside Docker / StackBlitz), Nuxt's internal vite-node IPC server binds to a Linux abstract-namespace Unix socket (`\0nuxt-vite-node-<pid>-<ts>.sock`). Abstract sockets have no filesystem inode and therefore no permission bits: any local UID on the host that can read `/proc/net/unix` can enumerate the socket and connect to it.

The IPC server does not perform any peer-credential or shared-secret check before dispatching requests. The `module` request type passes its `moduleId` field straight into Vite's SSR `fetchModule()`, which is not gated by Vite's HTTP-layer `server.fs.allow` deny-list. A co-resident unprivileged local user can therefore request paths like `/home/<dev>/project/.env?raw` or `~/.ssh/id_rsa?raw` and read the developer's secrets through the dev server's SSR plugin pipeline. The `resolve` request type additionally enables filesystem probing.

This affects developers running `nuxt dev` on shared multi-tenant Linux hosts (lab machines, shared bastions, CI runners shared between jobs without per-job container isolation). It does not affect:

- Production builds (`nuxt build` / `nuxt start`). The IPC server only runs in development.
- macOS or Windows developers.
- Docker / StackBlitz environments, which already fall back to a filesystem socket.
- Single-user laptops or per-job containerised CI.

### Patches

Fixed in `nuxt@4.4.7` (commit [`1f9f4767`](https://github.com/nuxt/nuxt/commit/1f9f4767a8725104da9bee872bb8d35246f25ae5)) and backported to `nuxt@3.21.7` (commit [`c293bf95`](https://github.com/nuxt/nuxt/commit/c293bf9503ccb3bc9559bff4a1f592f99063c9ea)).

The fix removes the abstract-namespace branch entirely. The IPC server now always binds to a filesystem Unix socket under the OS temp directory and explicitly `chmod 0600`s it after `listen()`, restricting connections to the owning UID. If the chmod fails for any reason, the server closes rather than serve requests on an unrestricted channel.

### Workarounds

If you cannot upgrade immediately on an affected host:

- Run `nuxt dev` inside a container or VM with no other tenants. Docker already triggers the filesystem-socket fallback in vulnerable versions and that fallback is unaffected.
- Bind the dev process to a single-user namespace (`unshare -U`, rootless containers).
- Restrict `/proc/net/unix` visibility via `hidepid=2` mount options where applicable, though this is partial mitigation only.

### References

- Affected file: `packages/vite/src/plugins/vite-node.ts`
- CWE-276: Incorrect Default Permissions

### Credit

Reported by Anthropic / Claude as part of Anthropic's coordinated vulnerability disclosure programme, reference ANT-2026-MSNKZFAT. Thanks to the Anthropic security team for the report and the detailed reproduction.

Independently reported by [@alcls01111](https://github.com/alcls01111) via GitHub's coordinated disclosure flow (`GHSA-5gvc-46gq-948j`), closed as a duplicate of this advisory.

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-534h-c3cw-v3h9
- https://github.com/nuxt/nuxt/commit/1f9f4767a8725104da9bee872bb8d35246f25ae5
- https://github.com/nuxt/nuxt/commit/c293bf9503ccb3bc9559bff4a1f592f99063c9ea
- https://github.com/nuxt/nuxt
