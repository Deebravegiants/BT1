# [C] CVE-2020-6018

## Summary
Severity: Critical
Advisory: CVE-2020-6018
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-02
Source: https://osv.dev/vulnerability/CVE-2020-6018
Type: osv

## Details
Valve's Game Networking Sockets prior to version v1.2.0 improperly handles long encrypted messages in function AES_GCM_DecryptContext::Decrypt() when compiled using libsodium, leading to a Stack-Based Buffer Overflow and resulting in a memory corruption and possibly even a remote code execution.

## References
- https://github.com/ValveSoftware/GameNetworkingSockets/commit/bea84e2844b647532a9b7fbc3a6a8989d66e49e3
- https://research.checkpoint.com/2020/game-on-finding-vulnerabilities-in-valves-steam-sockets/
