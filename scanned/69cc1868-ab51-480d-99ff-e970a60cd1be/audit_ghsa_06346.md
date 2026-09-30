# [M] AsyncHttpClient stores cookie for an unrelated domain (cookie tossing) via ThreadSafeCookieStore

## Summary
Severity: Medium
Advisory: GHSA-m452-q8c9-rg2f
CVE: CVE-2026-55688
CWE: CWE-1275
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-08-26
Source: https://github.com/advisories/GHSA-m452-q8c9-rg2f
Type: github-advisory

## Affected
- Maven: `org.asynchttpclient:async-http-client` — affected >=3.0.0.Beta1 <3.0.11
- Maven: `org.asynchttpclient:async-http-client` — affected >=2.0.0 <2.16.0

## Details
### Impact
 A **cookie tossing / cookie injection** issue (CWE-1275). `ThreadSafeCookieStore` stored a cookie under the value of its `Domain` attribute without verifying that the responding host is allowed to set a cookie for that domain (RFC 6265 §5.3 step 6). A host the client connects to can therefore plant a cookie scoped to an unrelated domain, and the client will then send that cookie on later requests to that domain.

### Who is Impacted
Applications that use a single `AsyncHttpClient` instance - and thus the default, shared `CookieStore` - to reach **both** an attacker-influenced host and a trusted host. Typical exposure: crawlers, link-preview / webhook fetchers, SSRF-style "fetch this URL" features, multi-backend aggregators, or following redirects to an attacker-controlled host. The attacker can *write* a cookie the client presents to the victim host (session fixation, overwriting a session id / CSRF-token cookie); they cannot *read* the victim host's cookies. Applications that talk only to a fixed trusted backend, or that disable/scope the cookie store, are not exposed.

### Patches
Fixed in 3.0.11 and 2.16.0

### Workarounds
- Disable the cookie store (setCookieStore(null)) when cookies are not needed; or
- Use a separate AsyncHttpClient (separate cookie store) per trust domain so an attacker-influenced host and a trusted host never share a jar
- Supply a custom CookieStore whose add(Uri, Cookie) rejects cookies whose Domain is not domain-matched by the request host.

## References
- https://github.com/AsyncHttpClient/async-http-client/security/advisories/GHSA-m452-q8c9-rg2f
- https://nvd.nist.gov/vuln/detail/CVE-2026-55688
- https://github.com/AsyncHttpClient/async-http-client/pull/2196
- https://github.com/AsyncHttpClient/async-http-client/pull/2199
- https://github.com/AsyncHttpClient/async-http-client/commit/8e4069cf3c92abe099db5fb13378ac2fe9e1fd3b
- https://github.com/AsyncHttpClient/async-http-client/commit/e6955c1e3951cf80e286981d064f6c926ce33f47
- https://github.com/AsyncHttpClient/async-http-client
- https://github.com/AsyncHttpClient/async-http-client/releases/tag/async-http-client-project-2.16.0
- https://github.com/AsyncHttpClient/async-http-client/releases/tag/async-http-client-project-3.0.11
- https://lists.debian.org/debian-lts-announce/2026/08/msg00011.html
