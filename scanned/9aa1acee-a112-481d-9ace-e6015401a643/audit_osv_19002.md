# [C] CVE-2020-6016

## Summary
Severity: Critical
Advisory: CVE-2020-6016
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-18
Source: https://osv.dev/vulnerability/CVE-2020-6016
Type: osv

## Details
Valve's Game Networking Sockets prior to version v1.2.0 improperly handles unreliable segments with negative offsets in function SNP_ReceiveUnreliableSegment(), leading to a Heap-Based Buffer Underflow and a free() of memory not from the heap, resulting in a memory corruption and probably even a remote code execution.

## References
- https://github.com/ValveSoftware/GameNetworkingSockets/commit/e0c86dcb9139771db3db0cfdb1fb8bef0af19c43
- https://research.checkpoint.com/2020/game-on-finding-vulnerabilities-in-valves-steam-sockets/
