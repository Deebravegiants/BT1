# [M] ALPINE-CVE-2016-6505

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-6505
Ecosystem: Alpine:v3.5
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6505
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=0 <2.0.5-r0

## Details
epan/dissectors/packet-packetbb.c in the PacketBB dissector in Wireshark 1.12.x before 1.12.13 and 2.x before 2.0.5 allows remote attackers to cause a denial of service (divide-by-zero error and application crash) via a crafted packet.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6505
