# [M] ALPINE-CVE-2024-52616

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-52616
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-11-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-52616
Type: osv

## Affected
- Alpine:v3.22: `avahi` — affected >=0 <0.8-r21
- Alpine:v3.23: `avahi` — affected >=0 <0.8-r21
- Alpine:v3.24: `avahi` — affected >=0 <0.8-r21

## Details
A flaw was found in the Avahi-daemon, where it initializes DNS transaction IDs randomly only once at startup, incrementing them sequentially after that. This predictable behavior facilitates DNS spoofing attacks, allowing attackers to guess transaction IDs.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-52616
