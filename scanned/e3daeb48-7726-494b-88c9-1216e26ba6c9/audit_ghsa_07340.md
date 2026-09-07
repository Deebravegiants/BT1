# [M] guzzlehttp/psr7: Host Confusion via Weak URI Host Validation

## Summary
Severity: Medium
Advisory: GHSA-c2w2-prh8-qm98
CVE: CVE-2026-59882
CWE: CWE-20, CWE-436
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-c2w2-prh8-qm98
Type: github-advisory

## Affected
- Packagist: `guzzlehttp/psr7` — affected >=0 <2.12.3

## Details
### Impact

`guzzlehttp/psr7` did not reject URI host components containing authority delimiters (`/`, `?`, `#`, `@`, or `\`), an embedded port such as `host:8080`, or IPv6 brackets that do not frame the host (such as `[::1` or `::1]`). `Uri::assertValidHost()` rejected only control characters, so these malformed hosts were accepted both when parsing a URI string — including through `new Uri()`, an absolute-form request target passed to `Message::parseRequest()`, and the synthetic `SERVER_NAME` or `SERVER_ADDR` fallback used by `ServerRequest::fromGlobals()` — and when setting a host with `Uri::withHost()`. Because the stored host was not validated, `Uri::getHost()` could return a value that does not agree with the URI's authority or with the host that is actually used on the wire. For example, `Uri::withHost('good.com@evil.com')` is accepted, and `new Uri('http://[gggg::1]/')` produces a `getHost()` of `'[gggg:'` while `getAuthority()` returns `'[gggg::1'`.

You are affected if your application builds a `Uri` or calls `Uri::withHost()` with host data that is wholly or partly attacker-controlled and then relies on `Uri::getHost()` for a security or routing decision, such as host allowlisting or denylisting, an SSRF guard, cookie scoping, or proxy-bypass selection. You are also affected if you parse, forward, proxy, or re-serialize URIs that come from untrusted raw HTTP messages or from synthetic `$_SERVER` values. Because `getHost()` can then disagree with the real connection target, the concrete impact depends on how your application and any downstream HTTP/1.x component use the URI, and may include host-based access-control bypass, server-side request forgery, routing to an unintended host, or `Host` header confusion. You are not affected if every host you place into a `Uri` is already trusted and well formed.

Applications using `guzzlehttp/guzzle` are affected in the same way through Guzzle's use of PSR-7. Guzzle derives the request `Host` header from the request URI, and its cookie matching and `no_proxy` proxy-bypass matching both read `Uri::getHost()`. An application that builds a Guzzle request URI from attacker-controlled host input can therefore have its `Host` header, cookie scope, or proxy-bypass decision computed against a host that differs from the one Guzzle connects to. This is not the normal request-sending path, and an application that passes only trusted, well-formed URIs to Guzzle and never builds a request URI from attacker-controlled host input is not affected through Guzzle's standard client APIs.

### Patches

The issue is patched in `2.12.3` and later. Starting in that release, `guzzlehttp/psr7` rejects URI host components that contain authority delimiters, an embedded port, or IPv6 brackets that do not frame the host, both when parsing a URI and via `Uri::withHost()`, so `Uri::getHost()` agrees with the URI authority. A framed bracketed literal whose contents are not a valid IPv6 address is preserved rather than rejected, so `getHost()` still agrees with the authority.

### Workarounds

If you cannot upgrade immediately, validate and normalize host values before you build or modify a `Uri` from untrusted input, and do not treat `Uri::getHost()` as a trust boundary for a host you have not independently checked. Before passing a host to `Uri`, reject any value that contains `/`, `?`, `#`, `@`, or `\`, that contains a colon outside a bracketed IPv6 literal, or that has unbalanced brackets. Applications that parse, forward, replay, or re-serialize raw HTTP messages, or that run with attacker-controlled `$_SERVER` values, should validate the host before calling `Message::parseRequest()` or `ServerRequest::fromGlobals()`, and should avoid reparsing untrusted input.

### References

* https://datatracker.ietf.org/doc/html/rfc3986#section-3.2.2
* https://datatracker.ietf.org/doc/html/rfc3986#section-3.2.3
* https://datatracker.ietf.org/doc/html/rfc6265#section-5.1.3

## References
- https://github.com/guzzle/psr7/security/advisories/GHSA-c2w2-prh8-qm98
- https://nvd.nist.gov/vuln/detail/CVE-2026-59882
- https://github.com/guzzle/psr7/pull/811
- https://github.com/guzzle/psr7/commit/ddd64f17d4cc1f7e5ffe6fd2c989ec7221712580
- https://github.com/guzzle/psr7
- https://github.com/guzzle/psr7/releases/tag/2.12.3
