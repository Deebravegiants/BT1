# [H] Vite Vulnerable to Arbitrary File Read via Vite Dev Server WebSocket

## Summary
Severity: High
Advisory: GHSA-p9ff-h696-f583
CVE: CVE-2026-39363
CWE: CWE-200, CWE-306
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-p9ff-h696-f583
Type: github-advisory

## Affected
- npm: `vite` — affected >=8.0.0 <8.0.5
- npm: `vite` — affected >=7.0.0 <7.3.2
- npm: `vite` — affected >=6.0.0 <6.4.2

## Details
### Summary

[`server.fs`](https://vite.dev/config/server-options#server-fs-strict) check was not enforced to the `fetchModule` method that is exposed in Vite dev server's WebSocket. 

### Impact

Only apps that match the following conditions are affected:

- explicitly exposes the Vite dev server to the network (using `--host` or [`server.host` config option](https://vitejs.dev/config/server-options.html#server-host))
- WebSocket is not disabled by `server.ws: false`

Arbitrary files on the server (development machine, CI environment, container, etc.) can be exposed.

### Details

If it is possible to connect to the Vite dev server’s WebSocket **without an `Origin` header**, an attacker can invoke `fetchModule` via the custom WebSocket event `vite:invoke` and combine `file://...` with `?raw` (or `?inline`) to retrieve the contents of arbitrary files on the server as a JavaScript string (e.g., `export default "..."`).

The access control enforced in the HTTP request path (such as `server.fs.allow`) is not applied to this WebSocket-based execution path.

### PoC

1. Start the dev server on the target 
   Example (used during validation with this repository):
   ```bash
   pnpm -C playground/alias exec vite --host 0.0.0.0 --port 5173
   ```

2. Confirm that access is blocked via the HTTP path (example: arbitrary file)
   ```bash
   curl -i 'http://localhost:5173/@fs/etc/passwd?raw'
   ```
   Result: `403 Restricted` (outside the allow list)
   <img width="3898" height="1014" alt="image" src="https://github.com/user-attachments/assets/f6593377-549c-45d7-b562-5c19833438af" />

3. Confirm that the same file can be retrieved via the WebSocket path
   By connecting to the HMR WebSocket without an `Origin` header and sending a `vite:invoke` request that calls `fetchModule` with a `file://...` URL and `?raw`, the file contents are returned as a JavaScript module.
  <img width="1049" height="296" alt="image" src="https://github.com/user-attachments/assets/af969f7b-d34e-4af4-8adb-5e2b83b31972" />
  <img width="1382" height="955" alt="image" src="https://github.com/user-attachments/assets/6a230d2e-197a-4c9c-b373-d0129756d5d7" />

## References
- https://github.com/vitejs/vite/security/advisories/GHSA-p9ff-h696-f583
- https://nvd.nist.gov/vuln/detail/CVE-2026-39363
- https://github.com/vitejs/vite/pull/22159
- https://github.com/vitejs/vite/commit/f02d9fde0b195afe3ea2944414186962fbbe41e0
- https://github.com/vitejs/vite
- https://github.com/vitejs/vite/releases/tag/v6.4.2
- https://github.com/vitejs/vite/releases/tag/v7.3.2
- https://github.com/vitejs/vite/releases/tag/v8.0.5
