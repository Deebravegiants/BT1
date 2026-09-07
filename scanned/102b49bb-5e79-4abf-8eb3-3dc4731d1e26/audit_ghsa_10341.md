# [M] AsyncHttpClient leaks authorization credentials to untrusted domains on cross-origin redirects

## Summary
Severity: Medium
Advisory: GHSA-cmxv-58fp-fm3g
CVE: CVE-2026-40490
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-cmxv-58fp-fm3g
Type: github-advisory

## Affected
- Maven: `org.asynchttpclient:async-http-client` — affected >=3.0.0.Beta1 <3.0.9
- Maven: `org.asynchttpclient:async-http-client` — affected >=2.0.0 <2.14.5

## Details
### Impact
When redirect following is enabled (followRedirect(true)), AsyncHttpClient forwards Authorization and Proxy-Authorization headers along with Realm credentials to arbitrary redirect targets regardless of domain, scheme, or port changes. This leaks credentials on cross-domain redirects and HTTPS-to-HTTP downgrades.

Additionally, even when stripAuthorizationOnRedirect is set to true, the Realm object containing plaintext credentials is still propagated to the redirect request, causing credential re-generation for Basic and Digest authentication schemes via NettyRequestFactory.

An attacker who controls a redirect target (via open redirect, DNS rebinding, or MITM on HTTP) can capture Bearer tokens, Basic auth credentials, or any other Authorization header value.

### Patches
Fixed in version 3.0.9 or 2.14.5. Users should upgrade immediately.

The fix automatically strips Authorization and Proxy-Authorization headers and clears Realm credentials whenever a redirect crosses origin boundaries (different scheme, host, or port) or downgrades from HTTPS to HTTP.

### Workarounds
For users unable to upgrade, set (stripAuthorizationOnRedirect(true)) in the client config and avoid using Realm-based authentication with redirect following enabled. Note that (stripAuthorizationOnRedirect(true)) alone is insufficient on versions prior to 3.0.9 or 2.14.5 because the Realm bypass still re-generates credentials.

Alternatively, disable redirect following (followRedirect(false)) and handle redirects manually with origin validation.

### References
 - Fix commit: https://github.com/AsyncHttpClient/async-http-client/commit/6b2fbb7f8

## References
- https://github.com/AsyncHttpClient/async-http-client/security/advisories/GHSA-cmxv-58fp-fm3g
- https://nvd.nist.gov/vuln/detail/CVE-2026-40490
- https://github.com/AsyncHttpClient/async-http-client/commit/6b2fbb7f8
- https://github.com/AsyncHttpClient/async-http-client/commit/ae557ad35246721c09dafb2976609cd0004e78ae
- https://github.com/AsyncHttpClient/async-http-client
- https://github.com/AsyncHttpClient/async-http-client/releases/tag/async-http-client-project-2.14.5
- https://github.com/AsyncHttpClient/async-http-client/releases/tag/async-http-client-project-3.0.9
