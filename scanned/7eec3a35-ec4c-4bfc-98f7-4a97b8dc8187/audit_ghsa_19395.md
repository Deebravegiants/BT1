# [M] Vite's server.fs.deny bypassed with /. for files under project root

## Summary
Severity: Medium
Advisory: GHSA-859w-5945-r5v3
CVE: CVE-2025-46565
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-30
Source: https://github.com/advisories/GHSA-859w-5945-r5v3
Type: github-advisory

## Affected
- npm: `vite` — affected >=6.3.0 <6.3.4
- npm: `vite` — affected >=6.2.0 <6.2.7
- npm: `vite` — affected >=6.0.0 <6.1.6
- npm: `vite` — affected >=5.0.0 <5.4.19
- npm: `vite` — affected >=0 <4.5.14

## Details
### Summary
The contents of files in [the project `root`](https://vite.dev/config/shared-options.html#root) that are denied by a file matching pattern can be returned to the browser.

### Impact

Only apps explicitly exposing the Vite dev server to the network (using --host or [server.host config option](https://vitejs.dev/config/server-options.html#server-host)) are affected.
Only files that are under [project `root`](https://vite.dev/config/shared-options.html#root) and are denied by a file matching pattern can be bypassed.

- Examples of file matching patterns: `.env`, `.env.*`, `*.{crt,pem}`, `**/.env`
- Examples of other patterns: `**/.git/**`, `.git/**`, `.git/**/*`

### Details
[`server.fs.deny`](https://vite.dev/config/server-options.html#server-fs-deny) can contain patterns matching against files (by default it includes `.env`, `.env.*`, `*.{crt,pem}` as such patterns).
These patterns were able to bypass for files under `root` by using a combination of slash and dot (`/.`).

### PoC
```
npm create vite@latest
cd vite-project/
cat "secret" > .env
npm install
npm run dev
curl --request-target /.env/. http://localhost:5173
```

![image](https://github.com/user-attachments/assets/822f4416-aa42-461f-8c95-a88d155e674b)
![image](https://github.com/user-attachments/assets/42902144-863a-4afb-ac5b-fc16effa37cc)

## References
- https://github.com/vitejs/vite/security/advisories/GHSA-859w-5945-r5v3
- https://nvd.nist.gov/vuln/detail/CVE-2025-46565
- https://github.com/vitejs/vite/commit/c22c43de612eebb6c182dd67850c24e4fab8cacb
- https://github.com/vitejs/vite
