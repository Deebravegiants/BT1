# [M] guzzlehttp/psr7 has Host Confusion via Authority Reinterpretation

## Summary
Severity: Medium
Advisory: GHSA-34xg-wgjx-8xph
CVE: CVE-2026-48998
CWE: CWE-20, CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-34xg-wgjx-8xph
Type: github-advisory

## Affected
- Packagist: `guzzlehttp/psr7` — affected >=0 <2.10.2

## Details
## Impact

`guzzlehttp/psr7` improperly interpreted malformed `Host` header values when constructing request URIs from inbound request data. This issue concerns inbound request parsing and server request construction. It does not require serializing a PSR-7 request, and it is not part of the normal outbound request-sending path used by `guzzlehttp/guzzle`.

A vulnerable flow is:

1. An attacker controls a raw HTTP request or server variable containing a `Host` value.
2. The `Host` value contains URI authority delimiters, such as `trusted.example@evil.example`.
3. `guzzlehttp/psr7` uses that value to construct a URI.
4. The URI parser treats the portion before `@` as userinfo and the portion after `@` as the URI host.
5. The resulting PSR-7 request URI host differs from the original `Host` header value.

For example, `Host: trusted.example@evil.example` can result in a PSR-7 URI whose host is `evil.example`, while the original Host header value remains `trusted.example@evil.example`.

Applications are affected if they parse attacker-controlled raw HTTP requests with `GuzzleHttp\Psr7\Message::parseRequest()` or the legacy 1.x `GuzzleHttp\Psr7\parse_request()` function, or if they build server requests from attacker-controlled server variables with `GuzzleHttp\Psr7\ServerRequest::fromGlobals()` or `GuzzleHttp\Psr7\ServerRequest::getUriFromGlobals()`, and then rely on the resulting URI host for routing, allow-list checks, credential selection, or forwarding decisions. Applications using `guzzlehttp/psr7` only through Guzzle's standard HTTP client APIs are not expected to be affected. In affected forwarding or gateway scenarios, this may cause requests or credentials to be sent to an unintended host.

## Patches

The issue is patched in `2.10.2` and later. `1.x` is end-of-life and will not receive a patch.

## Workarounds

If you cannot upgrade immediately, validate Host values before passing untrusted request data to `Message::parseRequest()`, legacy 1.x `parse_request()`, `ServerRequest::fromGlobals()`, or `ServerRequest::getUriFromGlobals()`.

Accept only `uri-host [ ":" port ]`. Reject values containing whitespace, control characters, userinfo (`@`), path (`/` or `\`), query (`?`), fragment (`#`), malformed IP literals or bracket syntax, or invalid port syntax.

Do not validate Host by prefixing it with `http://` and passing it to `parse_url()`, because that can reinterpret malformed values as URI userinfo and host.

## References

* https://www.rfc-editor.org/rfc/rfc9112.html#section-3.2
* https://www.rfc-editor.org/rfc/rfc9112.html#section-3.3
* https://www.rfc-editor.org/rfc/rfc9110.html#section-4.2.4
* https://www.rfc-editor.org/rfc/rfc9110.html#section-7.2

## References
- https://github.com/guzzle/psr7/security/advisories/GHSA-34xg-wgjx-8xph
- https://nvd.nist.gov/vuln/detail/CVE-2026-48998
- https://github.com/FriendsOfPHP/security-advisories/blob/master/guzzlehttp/psr7/CVE-2026-48998.yaml
- https://github.com/guzzle/psr7
