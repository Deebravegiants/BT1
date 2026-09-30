# [H] PocketMine-MP BookEditPacket crash when inventory slot in the packet is invalid

## Summary
Severity: High
Advisory: GHSA-xc7j-wj36-qjfr
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-xc7j-wj36-qjfr
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <5.11.2

## Details
### Summary
If a client sends a BookEditPacket with InventorySlot greater than 35, the server will crash due to an unhandled exception thrown by `BaseInventory->getItem()`.

### Details
Crashes at https://github.com/pmmp/PocketMine-MP/blob/b744e09352a714d89220719ab6948a010ac636fc/src/network/mcpe/handler/InGamePacketHandler.php#L873

### PoC
Using Gophertunnel, use `serverConn.WritePacket(&packet.BookEdit{InventorySlot: 36})`

### Impact
Server crash, all servers

### Patched versions
This issue was fixed by 47f011966092f275cc1b11f8de635e89fd9651a7, and the fix was released in 5.11.2.

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-xc7j-wj36-qjfr
- https://github.com/pmmp/PocketMine-MP/commit/47f011966092f275cc1b11f8de635e89fd9651a7
- https://github.com/pmmp/PocketMine-MP
- https://github.com/pmmp/PocketMine-MP/blob/b744e09352a714d89220719ab6948a010ac636fc/src/network/mcpe/handler/InGamePacketHandler.php#L873
