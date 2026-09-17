# [M] ALPINE-CVE-2024-34397

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-34397
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.2 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2024-05-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-34397
Type: osv

## Affected
- Alpine:v3.19: `glib` — affected >=2.79.0 <2.78.5-r0
- Alpine:v3.20: `glib` — affected >=2.79.0 <2.80.1-r0
- Alpine:v3.21: `glib` — affected >=2.79.0 <2.80.1-r0
- Alpine:v3.22: `glib` — affected >=2.79.0 <2.80.1-r0
- Alpine:v3.23: `glib` — affected >=2.79.0 <2.80.1-r0
- Alpine:v3.24: `glib` — affected >=2.79.0 <2.80.1-r0

## Details
An issue was discovered in GNOME GLib before 2.78.5, and 2.79.x and 2.80.x before 2.80.1. When a GDBus-based client subscribes to signals from a trusted system service such as NetworkManager on a shared computer, other users of the same computer can send spoofed D-Bus signals that the GDBus-based client will wrongly interpret as having been sent by the trusted system service. This could lead to the GDBus-based client behaving incorrectly, with an application-dependent impact.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-34397
