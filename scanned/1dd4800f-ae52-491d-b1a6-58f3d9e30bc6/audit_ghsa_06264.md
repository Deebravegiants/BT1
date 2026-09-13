# [H] Guzzle: Noncanonical host can bypass host-based checks

## Summary
Severity: High
Advisory: GHSA-v5mv-p594-2x33
CVE: CVE-2026-69246
CWE: CWE-180, CWE-436, CWE-918, CWE-941
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-v5mv-p594-2x33
Type: github-advisory

## Affected
- Packagist: `guzzlehttp/guzzle` — affected >=0 <7.15.2
- Packagist: `guzzlehttp/guzzle` — affected >=8.0.0 <8.0.1

## Details
### Impact

In affected versions, Guzzle gives a transport the request URI as text and supplies the `Host` header separately. The cURL handlers set `CURLOPT_URL` to the URI exactly as written and push that `Host` into `CURLOPT_HTTPHEADER`; `StreamHandler` does the same through `fopen()`. libcurl then parses the authority itself, percent-decoding it and, on an IDN-capable build, applying IDNA mapping, and uses the result to resolve, connect, name the TLS peer and address a proxy `CONNECT`, while the supplied `Host` suppresses the aligned one it would have generated. In `http://127.0.0.%31/` the URI host is one `filter_var()` rejects as an IP literal, yet libcurl decodes it to `127.0.0.1` and reaches loopback with no DNS lookup while the server receives `Host: 127.0.0.%31`.

An attacker who influences a fetched URI can therefore reach a host the application's checks excluded and read whatever it exposes of the response. The same divergence moves Guzzle's own decisions onto a spelling the transport does not use: `no_proxy` selects proxy routing from the literal host, and `RedirectMiddleware` decides from it whether to strip `Authorization` and `Cookie`. The cookie middleware extracts `Set-Cookie` against the URI Guzzle produced, not the authority contacted, so for a raw divergent URI the cookie is stored under the URI host as written. Where Guzzle rewrote that URI but left a divergent `Host`, or where the caller supplied one, the cookie is stored under the canonical name and replayed by ordinary later requests to it. With a third-party `UriInterface`, a host of `blocked.example.com@127.0.0.1` reaches `127.0.0.1` through all three handlers and generates `Authorization: Basic` from userinfo the application never wrote.

Exploitation requires the application to build a request URI from untrusted input and to make a host decision before handing it to Guzzle. Applications that only fetch URIs they construct themselves are not affected, and an exact allowlist of canonical names ordinarily fails closed; the exposure is to denylists, private-range and IP-literal checks, and any check that treats an unresolvable name as safe. The raw Unicode class needs an IDNA transformation somewhere: either a libcurl built with IDN support or Guzzle's own `idn_conversion`, off by default on both branches, which rewrites the URI in `Client::buildUri()` before a handler sees it and leaves a prebuilt request's explicit `Host` as written, while a request the client builds derives that header from the rewritten URI and produces no divergence. Noncanonical numeric spellings such as `127.1`, `2130706433`, `0x7f000001` and `0177.0.0.1` remain accepted after the patch and reach whatever the transport reads them as, loopback or a routable public host, and the cURL and stream handlers can differ, so a check comparing a host against an address as text stays bypassable. Guzzle does not offer SSRF protection, and neither cache poisoning nor cross-tenant compromise was established.

### Patches

This is a summary; the patches are the authority. The issue is fixed in `7.15.2` and `8.0.1`, which validate the request host in all three built-in handlers before any network I/O. A URI host is rejected for a byte outside `0x21` to `0x7E`, a percent escape, a URI authority delimiter, unbalanced brackets, or numeric-looking parts followed by a trailing dot. That last rule is deliberately conservative and also refuses out-of-range forms libcurl keeps as names, such as `256.0.0.1.`. An explicit `Host` header must be printable ASCII, and on `7.15.2` free of percent escapes. The client also regenerates a derived `Host` when it rewrites the request URI. Versions before `7.15.2` and version `8.0.0` are affected.

### Workarounds

If you cannot upgrade, constrain the host yourself before handing a URI to Guzzle, and constrain any explicit `Host` header separately, on every redirect hop. The URI rule assumes `$uri` is a validated `GuzzleHttp\Psr7\Uri`, so re-parse a third-party `UriInterface` with `new Uri((string) $uri)` first.

```php
$host = $uri->getHost();

if (
    preg_match('/\A[\x21-\x7E]*\z/D', $host) !== 1
    || strpbrk($host, '%@/?#\\') !== false
    || substr($host, -1) === '.'
) {
    throw new RuntimeException('Refusing to fetch this URI host.');
}

if (
    preg_match('/\A[\x21-\x7E]*\z/D', $hostHeader) !== 1
    || strpos($hostHeader, '%') !== false
) {
    throw new RuntimeException('Refusing to send this Host header.');
}
```

It differs from the patch in both directions: it refuses `example.com.`, which the patch accepts, and it does not canonicalize `127.1` or `0x7f000001`. Reparsing the URI separates a valid port from the host and rejects malformed bracket forms, so the snippet checks the host component alone. `idn_conversion => true` is not an access control, since IDNA maps `１２７。０。０。１` onto `127.0.0.1` and direct handler use bypasses it, and `Uri::getHost()` is not an SSRF boundary: it is the host as written, not the host a transport connects to. Where the destination matters, resolve the host and check the addresses, and use a separate cookie jar for untrusted origins.

## References
- https://github.com/guzzle/guzzle/security/advisories/GHSA-v5mv-p594-2x33
- https://github.com/guzzle/guzzle/pull/3907
- https://github.com/guzzle/guzzle/pull/3908
- https://github.com/guzzle/guzzle/commit/3aeea0406aab88cbbd86531313d7cebf8ae149a4
- https://github.com/guzzle/guzzle/commit/744101956d78b7c1384d0cbf379db13e859167bf
- https://github.com/guzzle/guzzle
- https://github.com/guzzle/guzzle/releases/tag/7.15.2
- https://github.com/guzzle/guzzle/releases/tag/8.0.1
