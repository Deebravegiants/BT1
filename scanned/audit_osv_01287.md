# [H] ALPINE-CVE-2018-9260

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-9260
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-9260
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=2.2.0 <2.2.14-r0

## Details
In Wireshark 2.4.0 to 2.4.5 and 2.2.0 to 2.2.13, the IEEE 802.15.4 dissector could crash. This was addressed in epan/dissectors/packet-ieee802154.c by ensuring that an allocation step occurs.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-9260
