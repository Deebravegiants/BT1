# [M] vite allows server.fs.deny bypass via backslash on Windows

## Summary
Severity: Medium
Advisory: GHSA-93m4-6634-74q7
CVE: CVE-2025-62522
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-20
Source: https://github.com/advisories/GHSA-93m4-6634-74q7
Type: github-advisory

## Affected
- npm: `vite` — affected >=7.1.0 <7.1.11
- npm: `vite` — affected >=7.0.0 <7.0.8
- npm: `vite` — affected >=6.0.0 <6.4.1
- npm: `vite` — affected >=2.9.18 <5.4.21
- npm: `vite` — affected >=3.2.9 <5.4.21
- npm: `vite` — affected >=4.5.3 <5.4.21
- npm: `vite` — affected >=5.2.6 <5.4.21

## Details
### Summary
Files denied by [`server.fs.deny`](https://vitejs.dev/config/server-options.html#server-fs-deny) were sent if the URL ended with `\` when the dev server is running on Windows.

### Impact
Only apps that match the following conditions are affected:

- explicitly exposes the Vite dev server to the network (using --host or [`server.host` config option](https://vitejs.dev/config/server-options.html#server-host))
- running the dev server on Windows

### Details
`server.fs.deny` can contain patterns matching against files (by default it includes `.env`, `.env.*`, `*.{crt,pem}` as such patterns). These patterns were able to bypass by using a back slash(`\`). The root cause is that `fs.readFile('/foo.png/')` loads `/foo.png`.

### PoC
```shell
npm create vite@latest
cd vite-project/
cat "secret" > .env
npm install
npm run dev
curl --request-target /.env\ http://localhost:5173
```
<img width="1593" height="616" alt="image" src="https://github.com/user-attachments/assets/36212f4e-1d3c-4686-b16f-16b35ca9e175" />

## References
- https://github.com/vitejs/vite/security/advisories/GHSA-93m4-6634-74q7
- https://nvd.nist.gov/vuln/detail/CVE-2025-62522
- https://github.com/vitejs/vite/commit/f479cc57c425ed41ceb434fecebd63931b1ed4ed
- https://github.com/vitejs/vite
