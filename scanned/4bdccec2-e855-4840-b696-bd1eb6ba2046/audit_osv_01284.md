# [H] ALPINE-CVE-2018-9256

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-9256
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-9256
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=2.2.0 <2.2.14-r0

## Details
In Wireshark 2.4.0 to 2.4.5 and 2.2.0 to 2.2.13, the LWAPP dissector could crash. This was addressed in epan/dissectors/packet-lwapp.c by limiting the encapsulation levels to restrict the recursion depth.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-9256
