# [H] ALPINE-CVE-2017-5597

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-5597
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5597
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=0 <2.2.4-r0

## Details
In Wireshark 2.2.0 to 2.2.3 and 2.0.0 to 2.0.9, the DHCPv6 dissector could go into a large loop, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-dhcpv6.c by changing a data type to avoid an integer overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5597
