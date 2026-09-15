# [M] ALPINE-CVE-2025-10148

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-10148
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-09-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-10148
Type: osv

## Affected
- Alpine:v3.19: `curl` — affected >=8.11.0 <8.14.1-r2
- Alpine:v3.20: `curl` — affected >=8.11.0 <8.14.1-r2
- Alpine:v3.21: `curl` — affected >=8.11.0 <8.14.1-r2
- Alpine:v3.22: `curl` — affected >=8.11.0 <8.14.1-r2
- Alpine:v3.23: `curl` — affected >=8.11.0 <8.16.0-r0
- Alpine:v3.24: `curl` — affected >=8.11.0 <8.16.0-r0

## Details
curl's websocket code did not update the 32 bit mask pattern for each new
 outgoing frame as the specification says. Instead it used a fixed mask that
persisted and was used throughout the entire connection.

A predictable mask pattern allows for a malicious server to induce traffic
between the two communicating parties that could be interpreted by an involved
proxy (configured or transparent) as genuine, real, HTTP traffic with content
and thereby poison its cache. That cached poisoned content could then be
served to all users of that proxy.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-10148
