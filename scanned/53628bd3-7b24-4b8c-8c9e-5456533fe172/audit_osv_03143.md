# [M] ALPINE-CVE-2024-52615

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-52615
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-11-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-52615
Type: osv

## Affected
- Alpine:v3.22: `avahi` — affected >=0 <0.8-r21
- Alpine:v3.23: `avahi` — affected >=0 <0.8-r21
- Alpine:v3.24: `avahi` — affected >=0 <0.8-r21

## Details
A flaw was found in Avahi-daemon, which relies on fixed source ports for wide-area DNS queries. This issue simplifies attacks where malicious DNS responses are injected.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-52615
