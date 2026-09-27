# [M] next-video: Unauthenticated arbitrary file read via /api/video request handler

## Summary
Severity: Medium
Advisory: GHSA-2p39-2jf3-fv2q
CVE: CVE-2026-54150
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-2p39-2jf3-fv2q
Type: github-advisory

## Affected
- npm: `next-video` — affected >=0 <2.8.1

## Details
### Impact

The HTTP route handler exported by `next-video/request-handler` — which the README instructs consumers to mount at `/api/video` — allows an unauthenticated remote attacker to read arbitrary `.json` files from the production filesystem of any application following the documented setup.

The handler's `GET` endpoint accepts a `url` query parameter and uses it to locate and serve a JSON asset descriptor from disk. The only guard between "remote URL" and "local file path" is a regex check for `^https?://`. Any value that does not match that prefix is treated as a local path, `.json` is appended, and the file is read with `fs.readFile` and returned in the HTTP response — with no authentication, no path canonicalization, and no traversal guard.

On a typical Next.js deployment this exposes, at minimum:
- The **Next.js Server Actions AES encryption key** (`.next/server/server-reference-manifest.json`)
- The **Next.js Preview/Draft Mode keys** (`previewModeId`, `previewModeSigningKey`, `previewModeEncryptionKey`)
- Internal build manifests, route registries, and absolute runtime paths
- Application-specific asset metadata (e.g. Mux `uploadId`, `assetId`, `playbackId` values stored in `videos/*.json`)

Any application that mounted `/api/video` following the documented one-liner is affected.

### Patches

2.8.1

### Workarounds

Until a patched version is available, wrap the exported handler in your own route file and validate the `url` parameter before passing it through:

- Reject any `url` value that does not begin with `https://`, or that does not match a known allowlist of trusted remote hosts.
- Alternatively, remove the `/api/video` route entirely if your application only uses build-time `import` of local video files and does not use `<Video src="https://...">` with string URLs at runtime.

### References

- `src/request-handler.ts` — the vulnerable GET handler
- `src/assets.ts` — `getAssetPath()`, where the local-vs-remote branching occurs
- `src/utils/utils.ts` — `isRemote()`, the sole guard between the two branches
- `src/config.ts` — `loadAsset()`, which performs the unconstrained `fs.readFile`

## References
- https://github.com/muxinc/next-video/security/advisories/GHSA-2p39-2jf3-fv2q
- https://github.com/muxinc/next-video/commit/73abf1d534c2ac48db546ecfed0e89cbaf124f6f
- https://github.com/muxinc/next-video
- https://github.com/muxinc/next-video/releases/tag/v2.8.1
