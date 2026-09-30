# [M] ALPINE-CVE-2026-71227

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-71227
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-71227
Type: osv

## Affected
- Alpine:v3.21: `libkcapi` — affected >=0.12.0 <1.5.1-r0
- Alpine:v3.22: `libkcapi` — affected >=0.12.0 <1.5.1-r0
- Alpine:v3.23: `libkcapi` — affected >=0.12.0 <1.5.1-r0
- Alpine:v3.24: `libkcapi` — affected >=0.12.0 <1.5.1-r0

## Details
A flaw was found in libkcapi. A local attacker can influence an application that uses the Asynchronous Input/Output (AIO) interface. By reusing an AIO-enabled handle after a prior completion error, the _kcapi_aio_read_all() function can enter a non-terminating wait loop. This can lead to a persistent denial of service, making the affected application or thread unresponsive.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-71227
