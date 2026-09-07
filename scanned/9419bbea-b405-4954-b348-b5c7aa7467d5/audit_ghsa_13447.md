# [H] PocketMine-MP vulnerable to server crash using badly formatted sign NBT in BlockActorDataPacket

## Summary
Severity: High
Advisory: GHSA-7wrv-6h42-w54f
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-07-14
Source: https://github.com/advisories/GHSA-7wrv-6h42-w54f
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=4.20.0 <4.22.3
- Packagist: `pocketmine/pocketmine-mp` — affected >=5.0.0 <5.2.1

## Details
### Summary
A player sending a packet can cause the server to crash by providing incorrect sign data in NBT in `BlockActorDataPacket`.

### Details
This vulnerability was discovered using the `BlockActorDataPacket`, but other packets may also be affected. The player would seem to just need to send an NBT with an incorrect type to throw this error.

```
[Server thread/CRITICAL]: pocketmine\nbt\UnexpectedTagTypeException: "Expected a tag of type pocketmine\nbt\tag\CompoundTag, got pocketmine\nbt\tag\ByteTag" (EXCEPTION) in "pmsrc/vendor/pocketmine/nbt/src/tag/CompoundTag" at line 107
--- Stack trace ---
  #0 pmsrc/src/network/mcpe/handler/InGamePacketHandler(751): pocketmine\nbt\tag\CompoundTag->getCompoundTag(string[9] FrontText)
  #1 pmsrc/vendor/pocketmine/bedrock-protocol/src/BlockActorDataPacket(50): pocketmine\network\mcpe\handler\InGamePacketHandler->handleBlockActorData(object pocketmine\network\mcpe\protocol\BlockActorDataPacket#220241)
  #2 pmsrc/src/network/mcpe/NetworkSession(433): pocketmine\network\mcpe\protocol\BlockActorDataPacket->handle(object pocketmine\network\mcpe\handler\InGamePacketHandler#190572)
```

### PoC
Use a bot or proxy to send a packet when editing a sign. This packet should contain an NBT with incorrect types but correct architecture.

### Impact
This makes it possible to shutdown a server for someone who knows how to operate it. As this was discovered in 4.22.1, everyone with at least this version is affected.

### Patches
This bug was fixed by 0c250a2ef09627b48aa52302f6cc7e1f2afb70ea in the 4.22.3 and 5.2.1 releases.

### Workarounds
A plugin may be able to handle `DataPacketReceiveEvent` for `BlockActorDataPacket`, and verify that the `FrontText` tag is a `TAG_Compound`.

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-7wrv-6h42-w54f
- https://github.com/pmmp/PocketMine-MP/commit/0c250a2ef09627b48aa52302f6cc7e1f2afb70ea
- https://github.com/pmmp/PocketMine-MP
