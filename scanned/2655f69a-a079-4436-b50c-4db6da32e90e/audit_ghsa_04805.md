# [M] Hono: app.mount() strips mount prefix using undecoded path, causing incorrect routing for percent-encoded paths

## Summary
Severity: Medium
Advisory: GHSA-2gcr-mfcq-wcc3
CVE: CVE-2026-47676
CWE: CWE-444, CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-2gcr-mfcq-wcc3
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.21

## Details
### Summary

`app.mount()` strips the mount prefix from the incoming request path using the raw URL pathname, while route matching is performed against the percent-decoded path. This inconsistency causes the prefix to be stripped at the wrong position when the path contains percent-encoded multi-byte characters, resulting in the mounted sub-application receiving an incorrect path.

### Details

When `app.mount(prefix, subApp)` is called, Hono calculates the number of characters to strip based on the decoded mount prefix length, but then applies that slice to the raw URL pathname. When the URL contains percent-encoded characters that expand to fewer characters when decoded (such as encoded non-ASCII characters), the two representations have different lengths, so the prefix is stripped at the wrong byte offset.

As a result, the sub-application receives a path that does not correspond to the intended sub-path — it may receive a partial or garbled path instead of the expected value after the mount prefix is removed.

This issue arises when an application uses `app.mount()` with paths that contain percent-encoded characters, particularly when the mount prefix itself or the request path contains encoded non-ASCII characters.

### Impact

A mounted sub-application may receive an incorrectly stripped path, causing requests to be routed to unintended handlers within the sub-application.

This may lead to:

- Middleware or route handlers in the sub-application being bypassed or incorrectly matched due to the malformed path
- Requests reaching sub-application routes that the developer did not intend to be accessible via the mounted path

This issue affects applications that use `app.mount()` where the request URL may contain percent-encoded characters in the mount prefix or subsequent path segments.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-2gcr-mfcq-wcc3
- https://nvd.nist.gov/vuln/detail/CVE-2026-47676
- https://github.com/honojs/hono/commit/6cbb025ff87fca1a3d00d0ccca0eaf3a6385c3f1
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.12.21
