# [H] vite: `server.fs.deny` bypass on Windows alternate paths

## Summary
Severity: High
Advisory: GHSA-fx2h-pf6j-xcff
CVE: CVE-2026-53571
CWE: CWE-200, CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-fx2h-pf6j-xcff
Type: github-advisory

## Affected
- npm: `vite` — affected >=8.0.0 <8.0.16
- npm: `vite` — affected >=7.0.0 <7.3.5
- npm: `vite` — affected >=0 <6.4.3
- npm: `vite-plus` — affected >=0 <0.1.24

## Details
### Summary

The contents of files that are specified by [`server.fs.deny`](https://vite.dev/config/server-options#server-fs-deny) can be returned to the browser on Windows.

### Impact

Only apps that match the following conditions are affected:

- explicitly exposes the Vite dev server to the network (using `--host` or [`server.host` config option](https://vitejs.dev/config/server-options.html#server-host))
- the sensitive file exists in the allowed directories specified by [`server.fs.allow`](https://vite.dev/config/server-options#server-fs-allow)
- either of:
  - the sensitive file exists in an NTFS volume
  - the dev server is running on Windows and the sensitive file exists in a volume that 8.3 short name generation is enabled (it is enabled by default on system volumes)

### Details

Vite’s dev server denies direct access to sensitive files through `server.fs.deny`, including entries such as `.env`, `.env.*`, and `*.{crt,pem}`. However, on Windows, the deny logic does not correctly normalize NTFS ADS path forms before access checks are applied.
Because of this, requests such as `/.env::$DATA?raw` are treated as allowed paths, while Windows resolves them to the original file's default data stream.

Similar to that, Windows allows accessing a file using a different name with the 8.3 short name compatibility feature. Vite did not reject accessing files via them.

### PoC
```bash
$ npm create vite@latest
$ cd vite-project/
$ npm install
$ npm run dev
```
Access via browser at `http://localhost:5173/.env::$DATA?raw`
<img width="388" height="129" alt="deecc1315123883cfd0f9c26a002845a" src="https://github.com/user-attachments/assets/895c6012-4e2e-4a35-babb-69bbf3ee7170" />

Example expected result:
- `/.env::$DATA?raw` returns the contents of `.env`
- `/tls.pem::$DATA?raw` returns the contents of `tls.pem`

## References
- https://github.com/vitejs/vite/security/advisories/GHSA-fx2h-pf6j-xcff
- https://nvd.nist.gov/vuln/detail/CVE-2026-53571
- https://github.com/vitejs/vite
