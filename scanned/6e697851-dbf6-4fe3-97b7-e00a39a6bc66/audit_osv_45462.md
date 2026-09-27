# [C] A use-after-free vulnerability exists in libcurl when an application configures an HTTP/2 stream...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1197
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1197
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.5.0+0 <8.21.0+0
- Julia: `LibCURL_jll` — affected >=7.88.1+0 <8.21.0+0

## Details
A use-after-free vulnerability exists in libcurl when an application
configures an HTTP/2 stream-dependency tree via `CURLOPT_STREAM_DEPENDS` or
`CURLOPT_STREAM_DEPENDS_E`, subsequently invokes `curl_easy_reset()`, and
finally terminates the handle with `curl_easy_cleanup()`. During this final
cleanup phase, libcurl attempts to access and modify an internal structure
that was already freed during the reset operation.

## References
- https://curl.se/docs/CVE-2026-10536.html
- https://curl.se/docs/CVE-2026-10536.json
- https://github.com/advisories/GHSA-wjq8-x4qm-6mmh
- https://hackerone.com/reports/3751697
- https://nvd.nist.gov/vuln/detail/CVE-2026-10536
