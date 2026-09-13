# [H] UAF after pause in socket callback

## Summary
Severity: High
Advisory: CVE-2026-9080
Aliases: CURL-CVE-2026-9080
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-9080
Type: osv

## Details
Calling `curl_easy_pause()` within the event-based `CURLMOPT_SOCKETFUNCTION`
callback triggers a use-after-free vulnerability, where libcurl attempts to
store a flag using a dangling struct pointer immediately after that pointer's
memory has been freed.

## References
- https://curl.se/docs/CVE-2026-9080.html
- https://curl.se/docs/CVE-2026-9080.json
- https://hackerone.com/reports/3749204
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9080.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-9080
