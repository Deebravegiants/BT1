# [M] ALPINE-CVE-2023-27538

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-27538
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-03-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-27538
Type: osv

## Affected
- Alpine:v3.14: `curl` — affected >=0 <8.0.1-r0
- Alpine:v3.15: `curl` — affected >=0 <8.0.1-r0
- Alpine:v3.16: `curl` — affected >=0 <8.0.1-r0
- Alpine:v3.17: `curl` — affected >=0 <7.88.1-r1
- Alpine:v3.18: `curl` — affected >=0 <8.0.0-r0
- Alpine:v3.19: `curl` — affected >=0 <8.0.0-r0
- Alpine:v3.20: `curl` — affected >=0 <8.0.0-r0
- Alpine:v3.21: `curl` — affected >=0 <8.0.0-r0
- Alpine:v3.22: `curl` — affected >=0 <8.0.0-r0
- Alpine:v3.23: `curl` — affected >=0 <8.0.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.0.0-r0

## Details
An authentication bypass vulnerability exists in libcurl prior to v8.0.0 where it reuses a previously established SSH connection despite the fact that an SSH option was modified, which should have prevented reuse. libcurl maintains a pool of previously used connections to reuse them for subsequent transfers if the configurations match. However, two SSH settings were omitted from the configuration check, allowing them to match easily, potentially leading to the reuse of an inappropriate connection.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-27538
