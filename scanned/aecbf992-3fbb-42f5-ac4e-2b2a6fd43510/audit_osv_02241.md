# [M] ALPINE-CVE-2021-3502

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-3502
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3502
Type: osv

## Affected
- Alpine:v3.18: `avahi` — affected >=0 <0.8-r5
- Alpine:v3.19: `avahi` — affected >=0 <0.8-r5
- Alpine:v3.20: `avahi` — affected >=0 <0.8-r5
- Alpine:v3.21: `avahi` — affected >=0 <0.8-r5
- Alpine:v3.22: `avahi` — affected >=0 <0.8-r5
- Alpine:v3.23: `avahi` — affected >=0 <0.8-r5
- Alpine:v3.24: `avahi` — affected >=0 <0.8-r5

## Details
A flaw was found in avahi 0.8-5. A reachable assertion is present in avahi_s_host_name_resolver_start function allowing a local attacker to crash the avahi service by requesting hostname resolutions through the avahi socket or dbus methods for invalid hostnames. The highest threat from this vulnerability is to the service availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3502
