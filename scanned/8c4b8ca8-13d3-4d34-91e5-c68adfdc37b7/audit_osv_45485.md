# [H] Calling `curl_easy_pause()` within the event-based `CURLMOPT_SOCKETFUNCTION` callback triggers a...

## Summary
Severity: High
Advisory: JLSEC-2026-1219
Ecosystem: Julia
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1219
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.13.0+0 <8.21.0+0
- Julia: `LibCURL_jll` — affected >=8.13.0+0 <8.21.0+0

## Details
Calling `curl_easy_pause()` within the event-based `CURLMOPT_SOCKETFUNCTION`
callback triggers a use-after-free vulnerability, where libcurl attempts to
store a flag using a dangling struct pointer immediately after that pointer's
memory has been freed.

## References
- https://curl.se/docs/CVE-2026-9080.html
- https://curl.se/docs/CVE-2026-9080.json
- https://github.com/advisories/GHSA-hf34-v47h-w6m3
- https://hackerone.com/reports/3749204
- https://nvd.nist.gov/vuln/detail/CVE-2026-9080
