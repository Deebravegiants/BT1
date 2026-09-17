# [M] Vite has an `server.fs.deny` bypass with an invalid `request-target`

## Summary
Severity: Medium
Advisory: GHSA-356w-63v5-8wf4
CVE: CVE-2025-32395
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-11
Source: https://github.com/advisories/GHSA-356w-63v5-8wf4
Type: github-advisory

## Affected
- npm: `vite` — affected >=6.2.0 <6.2.6
- npm: `vite` — affected >=6.1.0 <6.1.5
- npm: `vite` — affected >=6.0.0 <6.0.15
- npm: `vite` — affected >=5.0.0 <5.4.18
- npm: `vite` — affected >=0 <4.5.13

## Details
### Summary
The contents of arbitrary files can be returned to the browser if the dev server is running on Node or Bun.

### Impact
Only apps with the following conditions are affected.

- explicitly exposing the Vite dev server to the network (using --host or [server.host config option](https://vitejs.dev/config/server-options.html#server-host))
- running the Vite dev server on runtimes that are not Deno (e.g. Node, Bun)

### Details

[HTTP 1.1 spec (RFC 9112) does not allow `#` in `request-target`](https://datatracker.ietf.org/doc/html/rfc9112#section-3.2). Although an attacker can send such a request. For those requests with an invalid `request-line` (it includes `request-target`), the spec [recommends to reject them with 400 or 301](https://datatracker.ietf.org/doc/html/rfc9112#section-3.2-4). The same can be said for HTTP 2 ([ref1](https://datatracker.ietf.org/doc/html/rfc9113#section-8.3.1-2.4.1), [ref2](https://datatracker.ietf.org/doc/html/rfc9113#section-8.3.1-3), [ref3](https://datatracker.ietf.org/doc/html/rfc9113#section-8.1.1-3)).

On Node and Bun, those requests are not rejected internally and is passed to the user land. For those requests, the value of [`http.IncomingMessage.url`](https://nodejs.org/docs/latest-v22.x/api/http.html#messageurl) contains `#`. Vite assumed `req.url` won't contain `#` when checking `server.fs.deny`, allowing those kinds of requests to bypass the check.

On Deno, those requests are not rejected internally and is passed to the user land as well. But for those requests, the value of `http.IncomingMessage.url` did not contain `#`. 

### PoC
```
npm create vite@latest
cd vite-project/
npm install
npm run dev
```
send request to read `/etc/passwd`
```
curl --request-target /@fs/Users/doggy/Desktop/vite-project/#/../../../../../etc/passwd http://127.0.0.1:5173
```

## References
- https://github.com/vitejs/vite/security/advisories/GHSA-356w-63v5-8wf4
- https://nvd.nist.gov/vuln/detail/CVE-2025-32395
- https://github.com/vitejs/vite/commit/175a83909f02d3b554452a7bd02b9f340cdfef70
- https://github.com/vitejs/vite
