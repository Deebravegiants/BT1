# [M] NocoDB: Server-Side Request Forgery via Base Migration URL

## Summary
Severity: Medium
Advisory: GHSA-h6vv-pcq8-7xm4
CVE: CVE-2026-53930
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-h6vv-pcq8-7xm4
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0

## Details
### Summary
The base-migration endpoint accepted a caller-supplied URL that the migration worker
dereferenced without enforcing protocol or destination, allowing scheme abuse
(`file:`, `ftp:`, etc.) and probing of internal HTTP destinations.

### Details
The `migrate` endpoint is restricted to the workspace owner role by ACL. The remaining
gaps were (a) protocol validation — the controller now parses `body.migrationUrl` as a
`URL` and rejects anything whose protocol is not `http:` or `https:` — and (b) private
destination filtering — the worker already runs through `useAgent(targetUrl)` from
`request-filtering-agent`, which blocks RFC 1918, loopback, and link-local at the
socket layer.

### Impact
With the workspace owner role, a malformed URL could be used to coerce the migration
worker into reading local files or talking to non-HTTP services; combined with the
HTTP-only filter, owner-supplied targets could not reach private ranges.

### Credit
This issue was reported by Devel Group Security Research Team through [@TREXNEGRO](https://github.com/TREXNEGRO).
It was independently reported by [@Lihfdgjr](https://github.com/Lihfdgjr) and [@bugbunny-research (https://github.com/bugbunny-research).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-h6vv-pcq8-7xm4
- https://nvd.nist.gov/vuln/detail/CVE-2026-53930
- https://github.com/nocodb/nocodb
