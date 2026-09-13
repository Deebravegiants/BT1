# [M] Netty Vulnerable to Cache Poisoning and Information Disclosure via CORS Vary Header Overwrite

## Summary
Severity: Medium
Advisory: GHSA-8c42-7qj2-3j46
CVE: CVE-2026-59903
CWE: CWE-524
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-8c42-7qj2-3j46
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http` — affected >=4.2.0.Final <4.2.17.Final
- Maven: `io.netty:netty-codec-http` — affected >=0 <4.1.137.Final

## Details
### Summary
Netty's `CorsHandler` silently overwrites existing `Vary` headers, enabling cache poisoning and sensitive information disclosure.

### Details
`io.netty.handler.codec.http.cors.CorsHandler#setVaryHeader` overwrites any existing Vary headers set by backend applications. 

```java
    private static void setVaryHeader(final HttpResponse response) {
        response.headers().set(HttpHeaderNames.VARY, HttpHeaderNames.ORIGIN);
    }
```

Because `set()` replaces all existing values for the header, if a backend application sets a `Vary` header (such as `Vary: Authorization` or `Vary: Cookie`) to ensure that intermediate caches (like CDNs) cache responses separately per user, the `CorsHandler` will overwrite it with `Vary: origin`. This causes the caching proxy to ignore the authorization context and cache the response based solely on the URL and Origin, allowing an attacker to retrieve another user's cached sensitive data.

### Impact
This is a Cache Poisoning vulnerability that leads to Information Disclosure. It impacts any Netty-based web application that uses the CorsHandler, sets its own Vary headers to manage caching of authenticated or user-specific responses (e.g., Vary: Authorization), and is deployed behind a caching proxy or CDN. The end-users of these applications are impacted, as their sensitive data may be leaked to unauthorized actors.

## References
- https://github.com/netty/netty/security/advisories/GHSA-8c42-7qj2-3j46
- https://github.com/netty/netty/pull/17213
- https://github.com/netty/netty/pull/17217
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.137.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.17.Final
