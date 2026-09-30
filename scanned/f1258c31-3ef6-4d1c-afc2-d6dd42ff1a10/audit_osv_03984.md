# [H] ALPINE-CVE-2026-9080

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-9080
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-9080
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=8.13.0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=8.13.0 <8.21.0-r0

## Details
Calling `curl_easy_pause()` within the event-based `CURLMOPT_SOCKETFUNCTION`
callback triggers a use-after-free vulnerability, where libcurl attempts to
store a flag using a dangling struct pointer immediately after that pointer's
memory has been freed.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-9080
