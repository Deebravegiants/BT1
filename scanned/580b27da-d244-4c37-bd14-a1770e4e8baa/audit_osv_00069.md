# [M] ALPINE-CVE-2016-1907

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-1907
Ecosystem: Alpine:v3.2
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2016-01-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-1907
Type: osv

## Affected
- Alpine:v3.2: `openssh` — affected >=0 <6.8_p1-r10

## Details
The ssh_packet_read_poll2 function in packet.c in OpenSSH before 7.1p2 allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via crafted network traffic.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-1907
