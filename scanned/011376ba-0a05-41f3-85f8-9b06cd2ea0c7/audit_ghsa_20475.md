# [H] Unchecked validity of Facing values in PlayerActionPacket

## Summary
Severity: High
Advisory: GHSA-xh99-hw7h-wf63
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-13
Source: https://github.com/advisories/GHSA-xh99-hw7h-wf63
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <4.0.6

## Details
### Impact
A remote attacker may crash a server by sending `PlayerActionPacket` with invalid facing values (e.g. negative), specifically with `START_BREAK` or `CRACK_BLOCK` actions, or with a `UseItemTransactionData` (typically in `InventoryTransactionPacket`).

### Patches
f126479c37ff00a717a828f5271cf8e821d12d6c

### Workarounds
Using a plugin, cancel `DataPacketReceiveEvent` if the packet is `PlayerActionPacket` and the facing is outside the range 0-5 when receiving START_BREAK or CRACK_BLOCK actions, or UseItemTransactionData. However, beware that negative values may be legitimate in some cases.

### For more information
If you have any questions or comments about this advisory:
* Email us at [team@pmmp.io](mailto:team@pmmp.io)

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-xh99-hw7h-wf63
- https://github.com/pmmp/PocketMine-MP/commit/f126479c37ff00a717a828f5271cf8e821d12d6c
- https://github.com/pmmp/PocketMine-MP
