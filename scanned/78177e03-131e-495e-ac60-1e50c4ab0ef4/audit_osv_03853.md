# [M] ALPINE-CVE-2026-56847

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-56847
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-56847
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.23.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.23.2-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.18.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.18.1-r0

## Details
A flaw in Node.js Permission Model enforcement allows `trace_events.createTracing().enable()` Writes Trace Logs Outside `--allow-fs-write`.

This can lead to confidentiality impact or bypass of the intended security boundary under affected configurations.

This vulnerability affects Node.js **22.x**, **24.x**, and **26.x**.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-56847
