# [H] ALPINE-CVE-2017-6014

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-6014
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-6014
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=0 <2.2.4-r1

## Details
In Wireshark 2.2.4 and earlier, a crafted or malformed STANAG 4607 capture file will cause an infinite loop and memory exhaustion. If the packet size field in a packet header is null, the offset to read from will not advance, causing continuous attempts to read the same zero length packet. This will quickly exhaust all system memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-6014
