# [M] Guzzle: Cookie Disclosure and Injection via IP-Address Domains

## Summary
Severity: Medium
Advisory: GHSA-g446-98w2-8p5w
CVE: CVE-2026-59883
CWE: CWE-200, CWE-346, CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-g446-98w2-8p5w
Type: github-advisory

## Affected
- Packagist: `guzzlehttp/guzzle` — affected >=0 <7.12.3

## Details
### Impact

`CookieJar` does not restrict a cookie scoped to an IP address to the exact host that set it. When a stored cookie's `Domain` attribute is an IPv4 literal (`Domain=192.168.0.1`), a bracketed IPv6 literal (`Domain=[::1]`), or a bare numeric value that denotes an IPv4 address (`Domain=1`, which is `0.0.0.1`), `SetCookie::matchesDomain()` applies ordinary subdomain (suffix) matching to it instead of requiring an exact host. The IP-address check inside `matchesDomain()` is applied only to the request host and never to the cookie's own domain, and response cookies that carry an explicit `Domain` attribute are stored as suffix-matchable. As a result Guzzle sends such a cookie to any host whose name ends in that value as a trailing label, for example sending a `Domain=192.168.0.1` cookie to `evil.192.168.0.1`, or a `Domain=1` cookie to `evil.1`. The same flaw lets a look-alike host store a cookie that Guzzle then sends to the bare IP address. Depending on how the receiving service interprets the cookie, the impact is cross-host cookie disclosure, cookie injection, or session fixation.

You are affected if your application uses Guzzle's cookie support, for example `new Client(['cookies' => true])` or an explicit `CookieJar`, reuses one cookie jar across more than one host or trust boundary, and that jar can hold a cookie scoped to an IP-address or bare-numeric host. To actually leak a cookie the application must also resolve and connect to a look-alike host whose name ends in the IP-address label, such as `evil.192.168.0.1`. Such names are not publicly registrable, so in practice an attacker needs some influence over name resolution, which is realistic on private, split-horizon, container, or development networks. You are not affected if you do not use Guzzle's cookie support, if you use a separate cookie jar per host or trust boundary, or if your jars never hold cookies scoped to IP-address or bare-numeric hosts. This issue is independent of public suffix list validation. Per RFC 6265, an IP-address cookie domain must match only the exact host that set it and must never match a subdomain.

### Patches

The issue is patched in `7.12.3` and later. Starting in that release, Guzzle matches an IPv4 literal, a bracketed IPv6 literal, or a bare-numeric cookie `Domain` only against the exact request host, and no longer applies subdomain suffix matching to them.

### Workarounds

If you cannot upgrade immediately, do not reuse one `CookieJar` instance across untrusted and trusted origins. Use a separate cookie jar per host or trust boundary, or disable cookie handling for requests to untrusted hosts, and avoid scoping cookies to IP-address or bare-numeric hosts. In particular, avoid `new Client(['cookies' => true])` for any client that may contact unrelated hosts at different trust levels, because that option creates a single shared jar for the whole client.

### References

* https://datatracker.ietf.org/doc/html/rfc6265#section-5.1.3
* https://datatracker.ietf.org/doc/html/rfc6265#section-5.3
* https://url.spec.whatwg.org/#concept-ipv4-parser

## References
- https://github.com/guzzle/guzzle/security/advisories/GHSA-g446-98w2-8p5w
- https://nvd.nist.gov/vuln/detail/CVE-2026-59883
- https://github.com/guzzle/guzzle/pull/3694
- https://github.com/guzzle/guzzle/commit/b9944c161b12d9ee9c9334cfc5b9659ecd7451f8
- https://github.com/guzzle/guzzle
- https://github.com/guzzle/guzzle/releases/tag/7.12.3
