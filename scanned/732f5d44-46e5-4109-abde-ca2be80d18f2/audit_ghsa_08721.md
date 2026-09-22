# [H] async-http-client: Cookie header not stripped on cross-origin redirect

## Summary
Severity: High
Advisory: GHSA-fmxf-pm6p-7xgm
CVE: CVE-2026-45300
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-fmxf-pm6p-7xgm
Type: github-advisory

## Affected
- Maven: `org.asynchttpclient:async-http-client` — affected >=3.0.0.Beta1 <3.0.10
- Maven: `org.asynchttpclient:async-http-client` — affected >=2.0.0 <2.15.0

## Details
## Summary

async-http-client leaks `Cookie` headers to cross-origin redirect targets. When following a redirect across a security boundary (different origin, or HTTPS→HTTP downgrade), the `propagatedHeaders()` method in `Redirect30xInterceptor.java` strips `Authorization` and `Proxy-Authorization` headers but does not strip `Cookie`, so session cookies and other sensitive cookie values are forwarded to the redirect target — which may be attacker-controlled.

## Details

The vulnerability is in `client/src/main/java/org/asynchttpclient/netty/handler/intercept/Redirect30xInterceptor.java`.

The caller computes `stripAuth` on each redirect:

```java
boolean sameBase    = request.getUri().isSameBase(newUri);
boolean stripAuth   = !sameBase || schemeDowngrade || stripAuthorizationOnRedirect;
// ...
requestBuilder.setHeaders(propagatedHeaders(request, realm, keepBody, stripAuth));
```

`stripAuth` is `true` whenever the redirect crosses an origin, downgrades the scheme, or the caller opted in via `AsyncHttpClientConfig#isStripAuthorizationOnRedirect()`.

In the vulnerable version, `propagatedHeaders()` only removes `Authorization` and `Proxy-Authorization` in that branch — `Cookie` is left untouched:

```java
private static HttpHeaders propagatedHeaders(Request request, Realm realm, boolean keepBody, boolean stripAuthorization) {
    HttpHeaders headers = request.getHeaders()
            .remove(HOST)
            .remove(CONTENT_LENGTH);

    if (!keepBody) {
        headers.remove(CONTENT_TYPE);
    }

    if (stripAuthorization || (realm != null && (realm.getScheme() == AuthScheme.NTLM
            || realm.getScheme() == AuthScheme.SCRAM_SHA_256))) {
        headers.remove(AUTHORIZATION)
                .remove(PROXY_AUTHORIZATION);
        // BUG: COOKIE is not removed here, so cookies leak across the security boundary.
    }
    return headers;
}
```

The companion test class `RedirectCredentialSecurityTest` covers `Authorization` / `Proxy-Authorization` stripping on cross-origin redirects and scheme downgrades, but has no coverage for `Cookie`, which is why the regression went unnoticed.

## Proof of concept

```java
import org.asynchttpclient.*;

AsyncHttpClient client = asyncHttpClient();

// trusted-api.com responds 302 -> https://evil.com
Request request = new RequestBuilder("GET")
        .setUrl("https://trusted-api.com/endpoint")
        .setHeader("Cookie", "session=abc123; csrf=xyz789; api_key=secret")
        .setHeader("Authorization", "Bearer token123")
        .build();

client.executeRequest(request).get();

// Request seen by evil.com after the redirect:
//   Authorization: <stripped>
//   Cookie:        session=abc123; csrf=xyz789; api_key=secret   <-- leaked
```

## Impact

- **Session hijacking** — leaked session cookies allow impersonation.
- **CSRF token theft** — CSRF tokens carried in cookies are disclosed.
- **API key theft** — API keys stored in cookies are disclosed.
- **Privacy** — tracking identifiers leak to third-party origins.

Realistic attack paths:

- Open-redirect in a trusted API endpoint.
- Compromised CDN or API gateway injecting redirects.
- MITM on a plaintext hop in the redirect chain.

## Fix

Add `COOKIE` to the headers removed alongside `AUTHORIZATION` / `PROXY_AUTHORIZATION` on the security-boundary branch:

```java
if (stripAuthorization) {
    headers.remove(AUTHORIZATION)
            .remove(PROXY_AUTHORIZATION)
            .remove(COOKIE);
} else if (realm != null && (realm.getScheme() == AuthScheme.NTLM
        || realm.getScheme() == AuthScheme.SCRAM_SHA_256)) {
    headers.remove(AUTHORIZATION)
            .remove(PROXY_AUTHORIZATION);
}
```

Note that the URI-scoped `CookieStore` will re-add any cookies that legitimately match the new target after `propagatedHeaders` returns, so legitimate cross-origin sessions tracked by the client are not broken.

Fixed in **3.0.10** and **2.15.0** by commit [`3b0e3e9e`](https://github.com/AsyncHttpClient/async-http-client/commit/3b0e3e9e).

## References
- https://github.com/AsyncHttpClient/async-http-client/security/advisories/GHSA-fmxf-pm6p-7xgm
- https://nvd.nist.gov/vuln/detail/CVE-2026-45300
- https://github.com/AsyncHttpClient/async-http-client/commit/3b0e3e9e
- https://github.com/AsyncHttpClient/async-http-client
- https://github.com/AsyncHttpClient/async-http-client/releases/tag/async-http-client-project-3.0.10
