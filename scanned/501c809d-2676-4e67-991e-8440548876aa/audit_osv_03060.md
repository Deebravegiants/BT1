# [M] ALPINE-CVE-2024-35195

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-35195
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:N)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-35195
Type: osv

## Affected
- Alpine:v3.18: `py3-requests` — affected >=0 <2.32.3-r0
- Alpine:v3.19: `py3-requests` — affected >=0 <2.32.3-r0
- Alpine:v3.20: `py3-requests` — affected >=0 <2.32.3-r0
- Alpine:v3.21: `py3-requests` — affected >=0 <2.32.3-r0
- Alpine:v3.22: `py3-requests` — affected >=0 <2.32.3-r0
- Alpine:v3.23: `py3-requests` — affected >=0 <2.32.3-r0
- Alpine:v3.24: `py3-requests` — affected >=0 <2.32.3-r0

## Details
Requests is a HTTP library. Prior to 2.32.0, when making requests through a Requests `Session`, if the first request is made with `verify=False` to disable cert verification, all subsequent requests to the same host will continue to ignore cert verification regardless of changes to the value of `verify`. This behavior will continue for the lifecycle of the connection in the connection pool. This vulnerability is fixed in 2.32.0.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-35195
