# [H] ALPINE-CVE-2017-7704

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-7704
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7704
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=0 <2.2.6-r0

## Details
In Wireshark 2.2.0 to 2.2.5, the DOF dissector could go into an infinite loop, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-dof.c by using a different integer data type and adjusting a return value.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7704
