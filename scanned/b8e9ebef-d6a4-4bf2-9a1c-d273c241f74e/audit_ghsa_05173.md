# [M] guzzlehttp/psr7 has CRLF Injection via URI Host Component

## Summary
Severity: Medium
Advisory: GHSA-hq7v-mx3g-29hw
CVE: CVE-2026-49214
CWE: CWE-113, CWE-20, CWE-93
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-hq7v-mx3g-29hw
Type: github-advisory

## Affected
- Packagist: `guzzlehttp/psr7` — affected >=0 <2.10.2

## Details
## Impact

`guzzlehttp/psr7` did not reject ASCII control characters, whitespace, or DEL in first-party URI host components. The issue requires a PSR-7 request to be serialized into a raw HTTP/1.x message, for example with `GuzzleHttp\Psr7\Message::toString()` or an equivalent custom serializer. Creating a `Uri`, `Request`, or other PSR-7 object alone is not sufficient. The malformed host must be copied into the serialized `Host` header without further validation.

A vulnerable flow is:

1. An application accepts a user-controlled URL.
2. The URL is used to construct a PSR-7 `Uri` or `Request`.
3. The host component contains CRLF or another header-unsafe character.
4. The request is serialized into a raw HTTP/1.x message without an explicit `Host` header.
5. The host is copied into the serialized `Host` header.
6. The serialized request is written to the network or otherwise processed by software that does not independently reject the malformed host.

In that flow, an attacker can cause the serialized request to contain additional attacker-controlled header lines. For example, a host containing `"\r\nX-Injected: yes"` can cause the generated `Host` header to span multiple HTTP header lines.

This is not the normal request-sending path used by `guzzlehttp/guzzle`. Applications using `guzzlehttp/psr7` only through Guzzle's standard HTTP client APIs are not expected to be affected. Applications are most likely to be affected when they manually serialize PSR-7 requests, forward raw HTTP messages, or use custom transports, proxying, crawling, webhook delivery, or similar request-dispatch code that serializes requests without independently validating URI hosts and header data. In deployments involving HTTP/1.1 connection reuse, proxies, gateways, or load balancers, this malformed serialized request may also contribute to request smuggling or cache poisoning, depending on how downstream components parse the request.

## Patches

The issue is patched in `2.10.2` and later. `1.x` is end-of-life and will not receive a patch.

## Workarounds

If you cannot upgrade immediately, validate and reject all untrusted URI strings before constructing PSR-7 `Uri` or `Request` instances. Reject input containing ASCII control characters, whitespace, or DEL, including CRLF, tab, space, NUL, or DEL characters:

```php
if (preg_match('/[\x00-\x20\x7F]/', $untrustedUrl)) {
    throw new \InvalidArgumentException('Insecure URL detected');
}
```

Applications that manually serialize or forward requests should also ensure the final HTTP client, transport, or serializer rejects invalid URI and header data before writing requests to the network.

## References

* https://www.rfc-editor.org/rfc/rfc9112.html#section-3.2
* https://www.rfc-editor.org/rfc/rfc9112.html#section-5
* https://www.rfc-editor.org/rfc/rfc9112.html#section-11.2
* https://www.rfc-editor.org/rfc/rfc9110.html#section-7.2

## References
- https://github.com/guzzle/psr7/security/advisories/GHSA-hq7v-mx3g-29hw
- https://nvd.nist.gov/vuln/detail/CVE-2026-49214
- https://github.com/FriendsOfPHP/security-advisories/blob/master/guzzlehttp/psr7/CVE-2026-49214.yaml
- https://github.com/guzzle/psr7
