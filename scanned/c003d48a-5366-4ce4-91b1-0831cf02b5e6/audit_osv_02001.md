# [M] ALPINE-CVE-2020-6750

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-6750
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-01-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-6750
Type: osv

## Affected
- Alpine:v3.11: `glib` — affected >=2.60.0 <2.62.5-r0
- Alpine:v3.12: `glib` — affected >=2.60.0 <2.62.5-r0
- Alpine:v3.13: `glib` — affected >=2.60.0 <2.62.5-r0
- Alpine:v3.14: `glib` — affected >=2.60.0 <2.62.5-r0
- Alpine:v3.15: `glib` — affected >=2.60.0 <2.62.5-r0
- Alpine:v3.16: `glib` — affected >=2.60.0 <2.62.5-r0
- Alpine:v3.17: `glib` — affected >=2.60.0 <2.62.5-r0
- Alpine:v3.18: `glib` — affected >=2.60.0 <2.62.5-r0
- Alpine:v3.19: `glib` — affected >=2.60.0 <2.62.5-r0
- Alpine:v3.20: `glib` — affected >=2.60.0 <2.62.5-r0
- Alpine:v3.21: `glib` — affected >=2.60.0 <2.62.5-r0
- Alpine:v3.22: `glib` — affected >=2.60.0 <2.62.5-r0
- Alpine:v3.23: `glib` — affected >=2.60.0 <2.62.5-r0
- Alpine:v3.24: `glib` — affected >=2.60.0 <2.62.5-r0

## Details
GSocketClient in GNOME GLib through 2.62.4 may occasionally connect directly to a target address instead of connecting via a proxy server when configured to do so, because the proxy_addr field is mishandled. This bug is timing-dependent and may occur only sporadically depending on network delays. The greatest security relevance is in use cases where a proxy is used to help with privacy/anonymity, even though there is no technical barrier to a direct connection. NOTE: versions before 2.60 are unaffected.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-6750
