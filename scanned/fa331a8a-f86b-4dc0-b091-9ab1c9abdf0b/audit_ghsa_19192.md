# [M] TShock allows chat while not fully connected, possible ban evasion

## Summary
Severity: Medium
Advisory: GHSA-f8mx-cwfh-7hr2
CWE: CWE-285
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-03
Source: https://github.com/advisories/GHSA-f8mx-cwfh-7hr2
Type: github-advisory

## Affected
- NuGet: `TShock` — affected >=0 <5.2.2

## Details
This issue was reported to TShock by @ohayo, but was found by the Discord user by the name of `sofurry.com`. Please note that this user **does not own this domain on the internet, just the discord handle**.

TShock overrides certain Terraria vanilla systems, including chat, and the connection handling, for its own purposes, like enforcing bans. When clients connect but do not complete the connection handshake (e.g., send message number 6), they can "exist" on the server, occupy a player slot, chat, and receive data from the server despite not being fully connected. Individuals who exploit this will be able to effectively harass the server, observe the server, and utilize server resources even if banned from the server.

For servers that operate with a proxy that strictly enforces the connection handshake/sequence, this is not an issue, but for smaller servers or servers running vanilla TShock this is an issue worth patching for.

PR body supplied by @ohayo (patch writer):

Terraria's standard server by default checks for bans upon the client sending the ConnectRequest packet, however, TShock instead chooses to check if the client connecting is banned upon the Request World Data packet.

A malicious client can easily just not send this packet, and still join the server even while being banned.
Also by not sending Request World Data, the malicious client is still able to receive all packets from the server & even chat. 

Other clients will not be notified of their join/leave but will be able to see them on the player list.
Leading to potential chat spam & "spying" on packets of players within the server.

## References
- https://github.com/Pryaxis/TShock/security/advisories/GHSA-f8mx-cwfh-7hr2
- https://github.com/Pryaxis/TShock/commit/134f80f5b8eac8929aa10f518c00970700d5913d
- https://github.com/Pryaxis/TShock
