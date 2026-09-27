# [H] ALPINE-CVE-2020-27153

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-27153
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.9
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2020-10-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-27153
Type: osv

## Affected
- Alpine:v3.10: `bluez` — affected >=0 <5.50-r5
- Alpine:v3.11: `bluez` — affected >=0 <5.52-r2
- Alpine:v3.12: `bluez` — affected >=0 <5.54-r6
- Alpine:v3.9: `bluez` — affected >=0 <5.50-r2

## Details
In BlueZ before 5.55, a double free was found in the gatttool disconnect_cb() routine from shared/att.c. A remote attacker could potentially cause a denial of service or code execution, during service discovery, due to a redundant disconnect MGMT event.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-27153
