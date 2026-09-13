# [M] ALPINE-CVE-2019-6474

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-6474
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-6474
Type: osv

## Affected
- Alpine:v3.17: `kea` — affected >=1.4.0 <1.7.2-r0
- Alpine:v3.18: `kea` — affected >=1.4.0 <1.7.2-r0
- Alpine:v3.19: `kea` — affected >=1.4.0 <1.7.2-r0
- Alpine:v3.20: `kea` — affected >=1.4.0 <1.7.2-r0
- Alpine:v3.21: `kea` — affected >=1.4.0 <1.7.2-r0
- Alpine:v3.22: `kea` — affected >=1.4.0 <1.7.2-r0
- Alpine:v3.23: `kea` — affected >=1.4.0 <1.7.2-r0
- Alpine:v3.24: `kea` — affected >=1.4.0 <1.7.2-r0

## Details
A missing check on incoming client requests can be exploited to cause a situation where the Kea server's lease storage contains leases which are rejected as invalid when the server tries to load leases from storage on restart. If the number of such leases exceeds a hard-coded limit in the Kea code, a server trying to restart will conclude that there is a problem with its lease store and give up. Versions affected: 1.4.0 to 1.5.0, 1.6.0-beta1, and 1.6.0-beta2

## References
- https://security.alpinelinux.org/vuln/CVE-2019-6474
