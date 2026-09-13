# [M] JLSEC-2026-761

## Summary
Severity: Medium
Advisory: JLSEC-2026-761
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/JLSEC-2026-761
Type: osv

## Affected
- Julia: `iperf_jll` — affected >=0 <3.21.0+0

## Details
iPerf3 before 3.17, when used with OpenSSL before 3.2.0 as a server with RSA authentication, allows a timing side channel in RSA decryption operations. This side channel could be sufficient for an attacker to recover credential plaintext. It requires the attacker to send a large number of messages for decryption, as described in "Everlasting ROBOT: the Marvin Attack" by Hubert Kario.

## References
- https://downloads.es.net/pub/iperf/esnet-secadv-2024-0001.txt.asc
- https://github.com/esnet/iperf/releases/tag/3.17
- https://lists.debian.org/debian-lts-announce/2025/01/msg00027.html
- https://security.netapp.com/advisory/ntap-20250228-0007/
- https://www.insyde.com/security-pledge/SA-2024005
