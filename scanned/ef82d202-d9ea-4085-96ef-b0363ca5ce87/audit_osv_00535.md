# [H] ALPINE-CVE-2017-15191

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-15191
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-15191
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=2.0.0 <2.2.10-r0

## Details
In Wireshark 2.4.0 to 2.4.1, 2.2.0 to 2.2.9, and 2.0.0 to 2.0.15, the DMP dissector could crash. This was addressed in epan/dissectors/packet-dmp.c by validating a string length.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-15191
