# [M] PocketMine-MP: Network amplification vulnerability with `ActorEventPacket`

## Summary
Severity: Medium
Advisory: GHSA-7hmv-4j2j-pp6f
CWE: CWE-406
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-7hmv-4j2j-pp6f
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <5.39.2

## Details
### Impact
The server handles `ActorEventPacket` to trigger consuming animations from vanilla clients when they eat food or drink potions.

This can be abused to make the server spam other clients, and to waste server CPU and memory. For every `ActorEventPacket` sent by the client, an animation event will be sent to every other player the attacker is visible to.

This is similar to various other vulnerabilities which were fixed in the network overhaul of PM4 (e.g. `AnimatePacket` and `LevelSoundEventPacket`), but somehow this one slipped through the net.

### Patches
The problem was addressed in aeea1150a772a005b92bd418366f1b7cf1a91ab5 by changing the mechanism for consuming animations to be fully controlled by the server. `ActorEventPacket` from the client is now discarded.

### Workarounds
A plugin could use `DataPacketDecodeEvent` to rate-limit `ActorEventPacket` to prevent the attack.

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-7hmv-4j2j-pp6f
- https://github.com/pmmp/PocketMine-MP/commit/aeea1150a772a005b92bd418366f1b7cf1a91ab5
- https://github.com/pmmp/PocketMine-MP
