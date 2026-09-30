# [M] Guzzle: Host-only cookie scope is not preserved

## Summary
Severity: Medium
Advisory: GHSA-wm3w-8rrp-j577
CVE: CVE-2026-67355
CWE: CWE-201, CWE-941
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-wm3w-8rrp-j577
Type: github-advisory

## Affected
- Packagist: `guzzlehttp/guzzle` — affected >=0 <7.15.1

## Details
### Impact

In affected versions, `CookieJar` does not preserve whether a response cookie was set without a `Domain` attribute or with an empty one. A cookie without `Domain` is host-only and must be returned only to the exact host that set it. Under current cookie processing rules, an empty `Domain` value is also host-only. Guzzle instead stores the request host in the cookie's `Domain` field and later applies ordinary domain matching, as though the server had supplied a valid domain. For example, a host-only `sid=secret` cookie set by `example.com` can subsequently be sent to `child.example.com`. `FileCookieJar` and `SessionCookieJar` also persist the request host without recording the host-only state, so reloading a jar preserves the widened scope.

An attacker who controls or can observe a child host can therefore receive cookies that were intended only for its parent host. Depending on the cookie, this can disclose session identifiers, authorization tokens, or other sensitive state. Exploitation requires the application to enable Guzzle's cookie support, reuse the same built-in cookie jar, receive a host-only cookie from a parent host, and later make a matching request to a less-trusted child host. The cookie's other restrictions still apply. Its path must match, a `Secure` cookie is sent only over a secure connection, and an expired cookie is not sent.

Applications that do not use Guzzle's cookie support are not affected. Applications are also not affected by this disclosure if they use a separate jar for every host or trust boundary, never request a less-trusted subdomain with the same jar, or only store cookies carrying a valid, non-empty `Domain` attribute. The incorrect behavior occurs between an otherwise valid parent host and its subdomains.

### Patches

The issue is patched in `7.15.1` and later. Starting in that release, Guzzle records whether a response cookie is host-only and matches it only against the exact host. The host-only flag is part of cookie identity for replacement and response-driven deletion. Cookies carrying a valid, non-empty `Domain` attribute retain their existing domain-matching behavior. A host-only cookie can coexist with an explicit-domain cookie having the same name, domain string, and path.

The built-in persistent jars now write a boolean `HostOnly` marker for every stored cookie record. They reject records where that marker is missing or is not a boolean, and validate all records before changing the live jar. Persisted cookie records written by an older version are therefore rejected rather than silently interpreted with an unsafe scope. Loading non-empty file or session data written without this marker throws a `RuntimeException` until the data is deleted, regenerated, or correctly annotated. Versions before `7.15.1` are affected.

### Workarounds

If you cannot upgrade immediately, do not reuse one `CookieJar` instance across parent and child hosts with different trust levels. Use a separate cookie jar for each host or trust boundary, disable cookie handling for requests to less-trusted hosts, or avoid making those requests through a client configured with a shared jar. In particular, avoid `new Client(['cookies' => true])` for a client that may contact both a trusted parent host and less-trusted subdomains, because that option creates one jar for the whole client.

When upgrading, delete or rotate existing `FileCookieJar` and `SessionCookieJar` data that contains cookie records written without a `HostOnly` marker. Records may instead be annotated manually only when the original presence or absence of the cookie's `Domain` attribute is known. The stored domain string is not sufficient to infer it safely.

### References

* https://www.rfc-editor.org/rfc/rfc10025.html#section-4.1.2.3
* https://www.rfc-editor.org/rfc/rfc10025.html#section-5.7
* https://www.rfc-editor.org/rfc/rfc10025.html#section-5.8.3

## References
- https://github.com/guzzle/guzzle/security/advisories/GHSA-wm3w-8rrp-j577
- https://nvd.nist.gov/vuln/detail/CVE-2026-67355
- https://github.com/guzzle/guzzle/pull/3901
- https://github.com/guzzle/guzzle/commit/7b68220d6543f6f80fe62e633361fc9d4ead14d4
- https://github.com/guzzle/guzzle
- https://github.com/guzzle/guzzle/releases/tag/7.15.1
- https://www.vulncheck.com/advisories/guzzlehttp-guzzle-before-host-only-cookie-scope
