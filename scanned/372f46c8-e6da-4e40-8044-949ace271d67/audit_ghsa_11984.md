# [H] OpenClaw: Remote media error responses could trigger unbounded memory allocation before failure

## Summary
Severity: High
Advisory: GHSA-4qwc-c7g9-4xcw
CVE: CVE-2026-35633
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-4qwc-c7g9-4xcw
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
Remote media HTTP error bodies were read without a hard size cap before failure handling, allowing unbounded allocation on error responses.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `81445a901091a5d27ef0b56fceedbe4724566438`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- src/media/fetch.ts now routes non-2xx failures through bounded prefix reads instead of buffering the whole error body.
- src/media/read-response-with-limit.ts enforces capped reads and truncates oversized snippets before surfacing failure text.

OpenClaw thanks @YLChen-007 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-4qwc-c7g9-4xcw
- https://nvd.nist.gov/vuln/detail/CVE-2026-35633
- https://github.com/openclaw/openclaw/commit/630f1479c44f78484dfa21bb407cbe6f171dac87
- https://github.com/openclaw/openclaw/commit/81445a901091a5d27ef0b56fceedbe4724566438
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-unbounded-memory-allocation-via-remote-media-error-responses
