# [M] ALPINE-CVE-2017-7700

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-7700
Ecosystem: Alpine:v3.5
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7700
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=2.0.0 <2.2.6-r0

## Details
In Wireshark 2.2.0 to 2.2.5 and 2.0.0 to 2.0.11, the NetScaler file parser could go into an infinite loop, triggered by a malformed capture file. This was addressed in wiretap/netscaler.c by ensuring a nonzero record size.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7700
