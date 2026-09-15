# [M] Guzzle: URI fragments disclosed in redirect Referer headers

## Summary
Severity: Medium
Advisory: GHSA-h95v-h523-3mw8
CVE: CVE-2026-67354
CWE: CWE-201, CWE-212
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-h95v-h523-3mw8
Type: github-advisory

## Affected
- Packagist: `guzzlehttp/guzzle` — affected >=0 <7.15.1

## Details
### Impact

When the optional `referer` redirect setting is enabled, affected versions of `RedirectMiddleware` can copy the fragment from the referring request URI into a generated `Referer` header. A URI fragment is the part after `#`. It is handled locally by the client and is not part of the HTTP request target, so the server handling the original request does not receive it. A generated `Referer` tells the redirect destination which URI led to the request. Guzzle correctly removes user information from that value, but retains the fragment when it follows a redirect to the same scheme, such as HTTPS to HTTPS. For example, an initial URI ending in `#secret` is sent without the fragment, but the redirect destination can receive a `Referer` ending in `#secret`. This behavior affects both the cURL and stream handlers.

An attacker who controls the redirect destination can read the fragment from the incoming header, including through request logs or application code. If the fragment contains a one-time login secret, access token, state value, or other private client data, it is disclosed to a server that was never meant to receive it. Exploitation requires the application to enable `allow_redirects.referer`, make a request to a URI with a sensitive fragment, and follow a same-scheme redirect to a less-trusted destination.

The `referer` setting is disabled by default. Applications that leave it disabled, do not put sensitive data in URI fragments, do not follow redirects, or only redirect within the same trust boundary are not affected. Guzzle already omits the generated header when the scheme changes. This issue is limited to the fragment's inclusion. Reducing the path and query on cross-origin redirects is a separate privacy policy question.

### Patches

The issue is patched in `7.15.1` and later. Starting in that release, Guzzle removes both user information and the fragment before generating a redirect `Referer` value. Other redirect behavior does not change. Guzzle retains the referring path and query, and continues to omit the header when the scheme changes. Versions before `7.15.1` are affected when the optional `referer` setting is enabled.

### Workarounds

If you cannot upgrade immediately, leave automatic Referer generation disabled. It is off by default. If redirect options are configured explicitly, ensure that `referer` is `false`:

```php
$client->request('GET', $uri, [
    'allow_redirects' => ['referer' => false],
]);
```

Alternatively, disable automatic redirects and follow trusted destinations manually, or remove the fragment from the request URI before sending a request that may redirect. Do not rely on the fact that fragments are absent from the initial HTTP request target, because the affected middleware can reintroduce them in the generated header.

### References

* https://www.rfc-editor.org/rfc/rfc9110.html#section-10.1.3
* https://www.rfc-editor.org/rfc/rfc3986.html#section-3.5
* https://www.rfc-editor.org/rfc/rfc9700.html#section-4.2.3

## References
- https://github.com/guzzle/guzzle/security/advisories/GHSA-h95v-h523-3mw8
- https://nvd.nist.gov/vuln/detail/CVE-2026-67354
- https://github.com/guzzle/guzzle/pull/3901
- https://github.com/guzzle/guzzle/commit/7b68220d6543f6f80fe62e633361fc9d4ead14d4
- https://github.com/guzzle/guzzle
- https://github.com/guzzle/guzzle/releases/tag/7.15.1
- https://www.vulncheck.com/advisories/guzzlehttp-guzzle-before-uri-fragment-disclosure-via-referer
