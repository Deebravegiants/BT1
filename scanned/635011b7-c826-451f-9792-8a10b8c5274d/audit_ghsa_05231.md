# [M] NocoDB: Server-Side Request Forgery via Spreadsheet Import Endpoint

## Summary
Severity: Medium
Advisory: GHSA-hmcr-rmjq-47qr
CVE: CVE-2026-53931
CWE: CWE-441, CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-hmcr-rmjq-47qr
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0

## Details
### Summary
The spreadsheet-import endpoint `axiosRequestMake` could be used as a generic
HTTP proxy. Before the fix it was reachable unauthenticated, and its
URL-extension allowlist was a regex tested against the full URL string, so
URLs whose query string ended in `.csv` (for example
`https://example.com/robots.txt?.csv`) satisfied the gate even though the
underlying request was for `robots.txt`.

### Details
Three layers of protection now apply to the endpoint:

- The controller is decorated with `@UseGuards(DataApiLimiterGuard, GlobalGuard)`
  and `@Acl('fetchViaUrl')`, so unauthenticated callers and callers without
  the editor role are rejected before the request body is processed.
- The extension allowlist is tested against `url.pathname` only. Callers can
  no longer satisfy the regex by appending a `.csv` suffix to the query
  string.
- The downstream axios call is wired to `useAgent(url)` from
  `request-filtering-agent`, which blocks RFC 1918, loopback, link-local,
  and other private destinations at the socket layer.

### Impact
Unauthenticated callers could previously coerce the NocoDB process to issue
HTTP requests on their behalf, including to internal services reachable from
the host. With the auth gate in place and the pathname-anchored extension
check combined with socket-layer destination filtering, the endpoint is no
longer usable as a generic proxy and can no longer reach private ranges.

### Credit
This issue was reported by the [GitHub Security Lab](https://securitylab.github.com/)
([@p-](https://github.com/p-), [@m-y-mo](https://github.com/m-y-mo)).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-hmcr-rmjq-47qr
- https://nvd.nist.gov/vuln/detail/CVE-2026-53931
- https://github.com/nocodb/nocodb
