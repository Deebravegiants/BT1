# [M] linuxfabrik-lib: fetch() forwards credential headers across a cross-origin redirect

## Summary
Severity: Medium
Advisory: GHSA-4jc5-g844-4x33
CVE: CVE-2026-67435
CWE: CWE-200, CWE-918
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-30
Source: https://github.com/advisories/GHSA-4jc5-g844-4x33
Type: github-advisory

## Affected
- PyPI: `linuxfabrik-lib` — affected >=0 <6.0.0

## Details
### Summary
`lib.url.fetch()` follows HTTP redirects (`follow_redirects=True`). httpx strips only `Authorization` and `Cookie` when a redirect crosses the origin, so any other caller-supplied credential header (a session token such as Redfish's `X-Auth-Token`, an API key, ...) was still sent to the redirect target. A malicious or redirect-capable server can therefore answer an authenticated request with a `3xx` to an attacker-chosen host and receive the credential (server-side request forgery + token disclosure). The pre-httpx `urllib` implementation was worse: it forwarded every header, including `Authorization`, across cross-host redirects.

### Impact
Any plugin that authenticates to a host with a non-standard auth header and follows that host's redirects can be coerced into sending the credential, and an authenticated request, to another host the monitoring server can reach. The concrete case is the Redfish checks (`X-Auth-Token`), but the flaw is in the shared `fetch()` and affects every consumer.

### Patches
Fixed in linuxfabrik-lib 6.0.0 (commit 6573ff9). On a cross-origin redirect (any scheme/host/port change other than a plain same-host HTTP-to-HTTPS upgrade) `fetch()` now keeps only benign transport headers and drops every other caller-supplied header, so credentials never follow a redirect to a different origin.

## References
- https://github.com/Linuxfabrik/monitoring-plugins/security/advisories/GHSA-4jc5-g844-4x33
- https://nvd.nist.gov/vuln/detail/CVE-2026-67435
- https://github.com/Linuxfabrik/lib/commit/6573ff9347e541200305d278d2663d2e54e052ff
- https://github.com/Linuxfabrik/lib/releases/tag/v6.0.0
- https://github.com/Linuxfabrik/monitoring-plugins
