# [H] ALPINE-CVE-2017-13766

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-13766
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-13766
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=0 <2.2.9-r0

## Details
In Wireshark 2.4.0 and 2.2.0 to 2.2.8, the Profinet I/O dissector could crash with an out-of-bounds write. This was addressed in plugins/profinet/packet-dcerpc-pn-io.c by adding string validation.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-13766
