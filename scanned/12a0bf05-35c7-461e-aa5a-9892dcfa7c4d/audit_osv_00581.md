# [H] ALPINE-CVE-2017-17085

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-17085
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-17085
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=0 <2.2.11-r0

## Details
In Wireshark 2.4.0 to 2.4.2 and 2.2.0 to 2.2.10, the CIP Safety dissector could crash. This was addressed in epan/dissectors/packet-cipsafety.c by validating the packet length.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-17085
