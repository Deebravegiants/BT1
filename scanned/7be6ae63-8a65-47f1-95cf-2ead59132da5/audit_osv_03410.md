# [C] ALPINE-CVE-2026-10536

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-10536
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-10536
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.88.0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=7.88.0 <8.21.0-r0

## Details
A use-after-free vulnerability exists in libcurl when an application
configures an HTTP/2 stream-dependency tree via `CURLOPT_STREAM_DEPENDS` or
`CURLOPT_STREAM_DEPENDS_E`, subsequently invokes `curl_easy_reset()`, and
finally terminates the handle with `curl_easy_cleanup()`. During this final
cleanup phase, libcurl attempts to access and modify an internal structure
that was already freed during the reset operation.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-10536
