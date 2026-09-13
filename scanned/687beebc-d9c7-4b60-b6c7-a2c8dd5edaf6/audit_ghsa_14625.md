# [C] AsyncHttpClient (AHC) library's `CookieStore` replaces explicitly defined `Cookie`s

## Summary
Severity: Critical
Advisory: GHSA-mfj5-cf8g-g2fv
CVE: CVE-2024-53990
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-mfj5-cf8g-g2fv
Type: github-advisory

## Affected
- Maven: `org.asynchttpclient:async-http-client` — affected >=2.1.0 <2.12.4
- Maven: `org.asynchttpclient:async-http-client` — affected >=3.0.0.Beta1 <3.0.1

## Details
### Summary

When making any HTTP request, the automatically enabled and self-managed `CookieStore` (aka cookie jar) will silently replace explicitly defined `Cookie`s with any that have the same name from the cookie jar. For services that operate with multiple users, this can result in one user's `Cookie` being used for another user's requests.

### Details

This issue is described without security warnings here:

https://github.com/AsyncHttpClient/async-http-client/issues/1964

A PR to fix this issue has been made:

https://github.com/AsyncHttpClient/async-http-client/pull/2033

### PoC

1. Add an auth `Cookie` to the `CookieStore`
    - This is identical to receiving an HTTP response that uses `Set-Cookie`, as shown in issue #1964 above.
2. Handle a different user's request where the same `Cookie` is provided as a passthrough, like a JWT, and attempt to use it by explicitly providing it.
3. Observe that the user's cookie in step 2 is passed as the Cookie in step 1.

### Impact

This is generally going to be a problem for developers of backend services that implement third party auth features and use other features like token refresh. The moment a third party service responds by _setting_ a cookie in the response, the `CookieStore` will effectively break almost every follow-up request (hopefully by being rejected, but possibly by revealing a different user's information).

If your service sets cookies based on the response that happens here, it's possible to lead to even greater levels of exposure.

### Workaroud

You can avoid this issue by disabling the `CookieStore` during client creation:

```java
DefaultAsyncHttpClientConfig.Builder clientBuilder = Dsl.config()
 .setCookieStore(null)
 // other configuration
 ;
```

## References
- https://github.com/AsyncHttpClient/async-http-client/security/advisories/GHSA-mfj5-cf8g-g2fv
- https://nvd.nist.gov/vuln/detail/CVE-2024-53990
- https://github.com/AsyncHttpClient/async-http-client/issues/1964
- https://github.com/AsyncHttpClient/async-http-client/pull/2033
- https://github.com/AsyncHttpClient/async-http-client/commit/d5a83362f7aed81b93ebca559746ac9be0f95425
- https://github.com/AsyncHttpClient/async-http-client
- https://github.com/AsyncHttpClient/async-http-client/blob/main/CHANGES.md#from-20-to-21
