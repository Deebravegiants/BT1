# [C] CVE-2020-6017

## Summary
Severity: Critical
Advisory: CVE-2020-6017
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-03
Source: https://osv.dev/vulnerability/CVE-2020-6017
Type: osv

## Details
Valve's Game Networking Sockets prior to version v1.2.0 improperly handles long unreliable segments in function SNP_ReceiveUnreliableSegment() when configured to support plain-text messages, leading to a Heap-Based Buffer Overflow and resulting in a memory corruption and possibly even a remote code execution.

## References
- https://github.com/ValveSoftware/GameNetworkingSockets/commit/e0c86dcb9139771db3db0cfdb1fb8bef0af19c43
- https://research.checkpoint.com/2020/game-on-finding-vulnerabilities-in-valves-steam-sockets/
