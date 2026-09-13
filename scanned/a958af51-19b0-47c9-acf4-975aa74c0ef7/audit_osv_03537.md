# [H] ALPINE-CVE-2026-27623

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-27623
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-27623
Type: osv

## Affected
- Alpine:v3.23: `valkey` — affected >=9.0.0 <9.0.3-r0
- Alpine:v3.24: `valkey` — affected >=9.0.0 <9.0.3-r0

## Details
Valkey is a distributed key-value database. Starting in version 9.0.0 and prior to version 9.0.3, a malicious actor with network access to Valkey can cause the system to abort by triggering an assertion. When processing incoming requests, the Valkey system does not properly reset the networking state after processing an empty request. A malicious actor can then send a request that the server incorrectly identifies as breaking server side invariants, which results in the server shutting down. Version 9.0.3 fixes the issue. As an additional mitigation, properly isolate Valkey deployments so that only trusted users have access.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-27623
