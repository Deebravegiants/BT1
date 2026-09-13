# [H] ALPINE-CVE-2018-11362

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-11362
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-11362
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=2.2.0 <2.2.15-r0

## Details
In Wireshark 2.6.0, 2.4.0 to 2.4.6, and 2.2.0 to 2.2.14, the LDSS dissector could crash. This was addressed in epan/dissectors/packet-ldss.c by avoiding a buffer over-read upon encountering a missing '\0' character.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-11362
