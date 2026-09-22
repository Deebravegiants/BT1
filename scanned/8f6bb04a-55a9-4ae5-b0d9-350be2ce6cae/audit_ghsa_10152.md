# [H] Vite: `server.fs.deny` bypassed with queries

## Summary
Severity: High
Advisory: GHSA-v2wj-q39q-566r
CVE: CVE-2026-39364
CWE: CWE-180, CWE-284
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-v2wj-q39q-566r
Type: github-advisory

## Affected
- npm: `vite` — affected >=8.0.0 <8.0.5
- npm: `vite` — affected >=7.1.0 <7.3.2

## Details
### Summary

The contents of files that are specified by [`server.fs.deny`](https://vite.dev/config/server-options#server-fs-deny) can be returned to the browser.

### Impact

Only apps that match the following conditions are affected:

- explicitly exposes the Vite dev server to the network (using `--host` or [`server.host` config option](https://vitejs.dev/config/server-options.html#server-host))
- the sensitive file exists in the allowed directories specified by [`server.fs.allow`](https://vite.dev/config/server-options#server-fs-allow)
- the sensitive file is denied with a pattern that matches a file by [`server.fs.deny`](https://vite.dev/config/server-options#server-fs-deny)

### Details

On the Vite dev server, files that should be blocked by `server.fs.deny` (e.g., `.env`, `*.crt`) can be retrieved with HTTP 200 responses when query parameters such as `?raw`, `?import&raw`, or `?import&url&inline` are appended.

### PoC

1. Start the dev server: `pnpm exec vite root --host 127.0.0.1 --port 5175 --strictPort`
2. Confirm that `server.fs.deny` is enforced (expect 403): `curl -i http://127.0.0.1:5175/src/.env | head -n 20`
   <img width="3944" height="1092" alt="image" src="https://github.com/user-attachments/assets/ecb9f2e0-e08f-4ac7-b194-e0f988c4cd4f" />
3. Confirm that the same files can be retrieved with query parameters (expect 200):
   <img width="2014" height="373" alt="image" src="https://github.com/user-attachments/assets/76bc2a6a-44f4-4161-ae47-eab5ae0c04a8" />

## References
- https://github.com/vitejs/vite/security/advisories/GHSA-v2wj-q39q-566r
- https://nvd.nist.gov/vuln/detail/CVE-2026-39364
- https://github.com/vitejs/vite/pull/22160
- https://github.com/vitejs/vite/commit/a9a3df299378d9cbc5f069e3536a369f8188c8ff
- https://github.com/vitejs/vite
- https://github.com/vitejs/vite/releases/tag/v7.3.2
- https://github.com/vitejs/vite/releases/tag/v8.0.5
