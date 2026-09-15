# [M] Hono: Unbounded dot-notation nesting in `parseBody()` can cause memory exhaustion

## Summary
Severity: Medium
Advisory: CVE-2026-84364
Aliases: GHSA-g6gw-c38x-mqfc
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84364
Type: osv

## Details
Hono is a Web application framework that provides support for any JavaScript runtime. Prior to 4.13.5, when parseBody() expands dot-separated form field names into nested objects with dot-notation parsing enabled, it does not limit the nesting depth or the total number of intermediate objects created. Empty segments are preserved, so one deeply dotted field name can encode one nesting level per byte, while a large number of shallowly dotted fields can create the same amplification across a request. A request body within a normal size limit can therefore allocate an object graph far larger than the request after the body has already been accepted. An unauthenticated attacker who can reach an affected endpoint can send concurrent requests that exhaust the JavaScript heap, terminate the server process, and leave the service unavailable until restart. Dot-notation parsing is not enabled by default, and applications using the default behavior are not affected. This issue is fixed in version 4.13.5.

## References
- https://github.com/honojs/hono/releases/tag/v4.13.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84364.json
- https://github.com/honojs/hono/security/advisories/GHSA-g6gw-c38x-mqfc
- https://nvd.nist.gov/vuln/detail/CVE-2026-84364
- https://github.com/honojs/hono/commit/531e9c5a3ae058d10de33f643055bd4009a87178
