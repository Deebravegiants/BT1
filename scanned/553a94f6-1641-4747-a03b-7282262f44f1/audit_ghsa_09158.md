# [M] sse-channel: SSE Injection via unsanitized event fields

## Summary
Severity: Medium
Advisory: GHSA-84hm-wfh8-c5pg
CVE: CVE-2026-44217
CWE: CWE-93
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-84hm-wfh8-c5pg
Type: github-advisory

## Affected
- npm: `sse-channel` — affected >=0 <4.0.1

## Details
### Impact

Implementations that allows user-provided values to be passed to `event`, `retry` or `id` fields would be susceptible to event spoofing, where an attacker could inject arbitrary messages into the stream.

- **Event Spoofing:** Attacker can inject arbitrary SSE events into the stream
- **Client-side Manipulation:** Injected events can trigger unintended behavior in frontend JavaScript EventSource listeners
- **Data Integrity:** Consumers of the SSE stream cannot distinguish injected events from legitimate ones

### Patches
Patch available in v4.0.1.

### Workarounds
Do not allow user data to control `event`, `retry` or `id` fields, and if you must - sanitize the input before passing it to `sse-channel`, stripping any newlines. 

### Resources

https://github.com/rexxars/sse-channel/issues/42

## References
- https://github.com/rexxars/sse-channel/security/advisories/GHSA-84hm-wfh8-c5pg
- https://nvd.nist.gov/vuln/detail/CVE-2026-44217
- https://github.com/rexxars/sse-channel/issues/42
- https://github.com/rexxars/sse-channel
