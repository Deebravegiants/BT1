# [H] ALPINE-CVE-2017-13765

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-13765
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-13765
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=2.0.0 <2.2.9-r0

## Details
In Wireshark 2.4.0, 2.2.0 to 2.2.8, and 2.0.0 to 2.0.14, the IrCOMM dissector has a buffer over-read and application crash. This was addressed in plugins/irda/packet-ircomm.c by adding length validation.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-13765
