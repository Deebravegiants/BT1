# [H] ALPINE-CVE-2017-15193

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-15193
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-15193
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=0 <2.2.10-r0

## Details
In Wireshark 2.4.0 to 2.4.1 and 2.2.0 to 2.2.9, the MBIM dissector could crash or exhaust system memory. This was addressed in epan/dissectors/packet-mbim.c by changing the memory-allocation approach.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-15193
