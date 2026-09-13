# [M] guzzlehttp/psr7: CRLF Injection in HTTP Start-Line Serialization

## Summary
Severity: Medium
Advisory: GHSA-vm85-hxw5-5432
CVE: CVE-2026-55766
CWE: CWE-113, CWE-93
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-vm85-hxw5-5432
Type: github-advisory

## Affected
- Packagist: `guzzlehttp/psr7` — affected >=0 <2.12.1

## Details
### Impact

`guzzlehttp/psr7` did not reject CR/LF characters in certain first-party HTTP start-line fields: the request method, protocol version, and response reason phrase. If an application placed attacker-controlled data into one of those fields and later serialized the PSR-7 message as raw HTTP/1.x, for example with `Message::toString()` or an equivalent serializer, the serialized message could contain attacker-controlled header lines. The issue can also be reached through `Message::parseRequest()` or `Message::parseResponse()` when malformed raw messages are parsed into first-party PSR-7 objects and then serialized again.

Creating or modifying a `Request`, `Response`, or other PSR-7 object alone is not sufficient. The issue requires the malformed message to be serialized and written to the network, forwarded, replayed, or otherwise processed by software that does not independently reject the malformed start line. This is not the normal request-sending path used by `guzzlehttp/guzzle`; applications using `guzzlehttp/psr7` only through Guzzle's standard HTTP client APIs are not expected to be affected.

Applications are most likely to be affected when they manually serialize PSR-7 messages, forward raw HTTP messages, or use custom transports, proxying, crawling, webhook delivery, testing, or similar code. Depending on how downstream HTTP/1.1 components parse the serialized message, this may lead to header injection, response splitting, request smuggling, or cache poisoning.

### Patches

The issue is patched in `2.12.1` and later. Starting in that release, `guzzlehttp/psr7` rejects CR/LF characters in HTTP method, protocol version, and response reason phrase values before storing them in first-party message objects.

### Workarounds

If you cannot upgrade immediately, reject CR/LF in untrusted method, protocol version, and reason phrase values before constructing or modifying PSR-7 messages.

Applications that parse, forward, replay, or serialize raw HTTP messages cannot work around the parser entry points by validating only after parsing. They should validate the raw start line before calling `Message::parseRequest()` or `Message::parseResponse()`, avoid reparsing untrusted raw messages, or upgrade. If an application runs with attacker-controlled synthetic `$_SERVER` values, validate `REQUEST_METHOD` and `SERVER_PROTOCOL` before calling `ServerRequest::fromGlobals()`.

## References
- https://github.com/guzzle/psr7/security/advisories/GHSA-vm85-hxw5-5432
- https://github.com/guzzle/psr7
