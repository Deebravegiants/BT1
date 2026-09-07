# [M] guzzlehttp/guzzle: Dot-Only Cookie Domains Match All Hosts

## Summary
Severity: Medium
Advisory: GHSA-cwxw-98qj-8qjx
CVE: CVE-2026-55767
CWE: CWE-1286, CWE-346
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-cwxw-98qj-8qjx
Type: github-advisory

## Affected
- Packagist: `guzzlehttp/guzzle` — affected >=0 <7.12.1

## Details
### Impact

`CookieJar` incorrectly accepts cookies with a dot-only `Domain` attribute, such as `Domain=.`, `Domain=..`, `Domain=...`, and whitespace-padded variants such as `Domain= . `. In affected versions, `SetCookie::matchesDomain()` removes leading dots from the cookie domain, normalizing dot-only values to the empty string; `SetCookie::validate()` only rejected a strictly empty domain, so these cookies could be stored and the empty normalized domain was treated as matching any request host.

An attacker-controlled origin that an application requests with a shared cookie jar can therefore set a cookie that Guzzle later sends to unrelated hosts using the same jar. This may allow cookie injection or session fixation against downstream services, depending on how those services interpret the injected cookie. Applications are affected when they use Guzzle's cookie support, for example `new Client(['cookies' => true])` or an explicit shared `CookieJar`, and reuse the same jar across attacker-controlled and trusted origins.

Applications that do not use Guzzle's cookie support, or that use separate cookie jars per origin or trust boundary, are not affected. This issue is distinct from public suffix list validation: dot-only domains contain no domain label and should not match unrelated hosts.

### Patches

The issue is patched in `7.12.1` and later. Starting in that release, Guzzle rejects dot-only cookie `Domain` attributes and prevents an empty normalized cookie domain from matching any request host.

### Workarounds

If you cannot upgrade immediately, do not reuse the same `CookieJar` instance across untrusted and trusted origins. Use separate cookie jars per origin or trust boundary, or disable cookie handling for requests to untrusted hosts.

Avoid using `new Client(['cookies' => true])` for clients that may contact unrelated hosts with different trust levels, because that option creates one shared jar for the client.

## References
- https://github.com/guzzle/guzzle/security/advisories/GHSA-cwxw-98qj-8qjx
- https://nvd.nist.gov/vuln/detail/CVE-2026-55767
- https://github.com/guzzle/guzzle/pull/3653
- https://github.com/guzzle/guzzle/commit/7f537cded1912349abf5081258d6db19106d774d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/guzzlehttp/guzzle/CVE-2026-55767.yaml
- https://github.com/guzzle/guzzle
- https://github.com/guzzle/guzzle/releases/tag/7.12.1
