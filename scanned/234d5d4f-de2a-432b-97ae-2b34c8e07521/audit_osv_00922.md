# [H] ALPINE-CVE-2018-11358

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-11358
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-11358
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=2.2.0 <2.2.15-r0

## Details
In Wireshark 2.6.0, 2.4.0 to 2.4.6, and 2.2.0 to 2.2.14, the Q.931 dissector could crash. This was addressed in epan/dissectors/packet-q931.c by avoiding a use-after-free after a malformed packet prevented certain cleanup.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-11358
