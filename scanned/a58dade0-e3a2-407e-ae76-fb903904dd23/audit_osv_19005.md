# [H] CVE-2020-6019

## Summary
Severity: High
Advisory: CVE-2020-6019
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-13
Source: https://osv.dev/vulnerability/CVE-2020-6019
Type: osv

## Details
Valve's Game Networking Sockets prior to version v1.2.0 improperly handles inlined statistics messages in function CConnectionTransportUDPBase::Received_Data(), leading to an exception thrown from libprotobuf and resulting in a crash.

## References
- https://github.com/ValveSoftware/GameNetworkingSockets/commit/d944a10808891d202bb1d5e1998de6e0423af678
- https://research.checkpoint.com/2020/game-on-finding-vulnerabilities-in-valves-steam-sockets/
