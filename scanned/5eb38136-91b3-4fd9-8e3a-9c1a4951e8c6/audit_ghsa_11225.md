# [M] Undici has Unbounded Memory Consumption in its DeduplicationHandler via Response Buffering that leads to DoS

## Summary
Severity: Medium
Advisory: GHSA-phc3-fgpg-7m6h
CVE: CVE-2026-2581
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-phc3-fgpg-7m6h
Type: github-advisory

## Affected
- npm: `undici` — affected >=7.17.0 <7.24.0

## Details
## Impact
This is an uncontrolled resource consumption vulnerability (CWE-400) that can lead to Denial of Service (DoS).

In vulnerable Undici versions, when `interceptors.deduplicate()` is enabled, response data for deduplicated requests could be accumulated in memory for downstream handlers. An attacker-controlled or untrusted upstream endpoint can exploit this with large/chunked responses and concurrent identical requests, causing high memory usage and potential OOM process termination.

Impacted users are applications that use Undici’s deduplication interceptor against endpoints that may produce large or long-lived response bodies.

## Patches

The issue has been patched by changing deduplication behavior to stream response chunks to downstream handlers as they arrive (instead of full-body accumulation), and by preventing late deduplication when body streaming has already started.

Users should upgrade to the first official Undici (and Node.js, where applicable) releases that include this patch.

## Workarounds
If upgrading immediately is not possible:

- Disable `interceptors.deduplicate()` for affected clients/routes.
- Use `skipHeaderNames` with a marker header to force high-risk requests to bypass deduplication.
- Avoid concurrent identical requests to untrusted endpoints that may return very large/chunked bodies.
- Apply upstream/proxy response-size and timeout limits.

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-phc3-fgpg-7m6h
- https://nvd.nist.gov/vuln/detail/CVE-2026-2581
- https://hackerone.com/reports/3513473
- https://cna.openjsf.org/security-advisories.html
- https://github.com/nodejs/undici
