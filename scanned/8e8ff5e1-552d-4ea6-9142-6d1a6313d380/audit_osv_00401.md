# [H] ALPINE-CVE-2017-11408

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-11408
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-11408
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=0 <2.2.8-r0

## Details
In Wireshark 2.2.0 to 2.2.7 and 2.0.0 to 2.0.13, the AMQP dissector could crash. This was addressed in epan/dissectors/packet-amqp.c by checking for successful list dissection.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-11408
