# [M] Server Side Request Forgery (SSRF) attack in Fedify

## Summary
Severity: Medium
Advisory: GHSA-p9cg-vqcc-grcx
CVE: CVE-2024-39687
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:L (CVSS_V3)
Published: 2024-07-05
Source: https://github.com/advisories/GHSA-p9cg-vqcc-grcx
Type: github-advisory

## Affected
- npm: `@fedify/fedify` — affected >=0 <0.9.2
- npm: `@fedify/fedify` — affected >=0.10.0 <0.10.2
- npm: `@fedify/fedify` — affected >=0.11.0 <0.11.2

## Details
### Summary
 
At present, when Fedify needs to retrieve an object or activity from a remote activitypub server, it makes a HTTP request to the `@id` or other resources present within the activity it has received from the web. This activity could reference an `@id` that points to an internal IP address, allowing an attacker to send request to resources internal to the fedify server's network.

This applies to not just resolution of documents containing activities or objects, but also to media URLs as well.

Specifically this is a [Server Side Request Forgery attack](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery). You can learn more about SSRF attacks via [CWE-918](https://cwe.mitre.org/data/definitions/918.html)

### Details

When Fedify makes a request at runtime via the DocLoader [1] [2], the `fetch` API does not first check the URI's to assert that it resolve to a public IP address. Additionally, any downstream software of Fedify that may fetch data from URIs contained within Activities or Objects maybe be at risk of requesting non-public resources, and storing those, exposing non-public information to the public.

Additionally, in many cases the URIs are not asserted to be either strictly HTTPS or HTTP protocols, which could lead to further attacks, and there is no check that the URI contains a `hostname` part. Whilst the [`fetch()` specification](https://fetch.spec.whatwg.org/) may provide some safety here, along with underlying fetch implementations, there is still potential for attacks through using `data:` URIs, or just attacking some other protocol entirely, e.g., FTP or CalDav.

[1] https://github.com/dahlia/fedify/blob/main/runtime/docloader.ts#L141
[2] https://github.com/dahlia/fedify/blob/main/runtime/docloader.ts#L175

#### Deno-specific Attack Vectors

In Deno specifically, the `fetch()` API allows [accessing local filesystem](https://docs.deno.com/deploy/api/runtime-fetch/), I'm not sure how Deno's [Permissions model](https://docs.deno.com/runtime/manual/runtime/permission_apis/) may prevent attacks utilising `file:` URIs.
 
> Fetch also supports fetching from file URLs to retrieve static files. For more info on static files, see the [filesystem API documentation](https://docs.deno.com/deploy/api/runtime-fs).

#### ActivityPub Security Considerations

This is also noted in the ActivityPub spec in [Section B.3 Security Considerations](https://www.w3.org/TR/activitypub/#security-localhost), however, there it is more limited in scope.

#### Other Implementations

It may be acceptable to allow a server operator to allow access to given non-public IP addresses, for instance [in Mastodon](https://github.com/mastodon/mastodon/blob/092bb8a27af9ee87ff9ebabaf354477470ea3a94/app/lib/request.rb#L330) they allow requests to non-public IP addresses, i.e., localhost in development and those in the `ALLOWED_PRIVATE_ADDRESSES` environment variable.

### PoC

I'm not sure a PoC is necessary given this is a reasonably well known vulnerability vector.

### Impact

This impacts server operates, as resources that are internal to their network may find themselves being improperly accessed or potentially even attacked or exposed to the public.

### Notes for resolution:

When implementing public IP address validation, be careful of [CWE-1389](https://cwe.mitre.org/data/definitions/1389.html) and [CWE-1286](https://cwe.mitre.org/data/definitions/1286.html) both of which [recently](https://github.com/advisories/GHSA-78xj-cgh5-2h22) caused a CVE to be filed against the popular node.js `ip` package, although this package was not originally intended for security purposes.

## References
- https://github.com/dahlia/fedify/security/advisories/GHSA-p9cg-vqcc-grcx
- https://nvd.nist.gov/vuln/detail/CVE-2024-39687
- https://github.com/dahlia/fedify/commit/30f9cf4a175704a04c874f3ea88414c5f1e00b28
- https://github.com/dahlia/fedify/commit/c641e976089dd913f649889c1bfb016df04e86ba
- https://github.com/dahlia/fedify
- https://github.com/dahlia/fedify/releases/tag/0.11.1
