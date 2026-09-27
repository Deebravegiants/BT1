# [C] HTTP/2 stream-dependency tree UAF

## Summary
Severity: Critical
Advisory: CVE-2026-10536
Aliases: CURL-CVE-2026-10536
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-10536
Type: osv

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
- https://hackerone.com/reports/3751697
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10536.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-10536
