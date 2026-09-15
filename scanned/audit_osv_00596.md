# [H] ALPINE-CVE-2017-17997

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-17997
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-17997
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=0 <2.2.12-r0

## Details
In Wireshark before 2.2.12, the MRDISC dissector misuses a NULL pointer and crashes. This was addressed in epan/dissectors/packet-mrdisc.c by validating an IPv4 address. This vulnerability is similar to CVE-2017-9343.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-17997
