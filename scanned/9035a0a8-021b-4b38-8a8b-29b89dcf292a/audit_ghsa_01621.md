# [H] Exploitable inventory component chaining in PocketMine-MP

## Summary
Severity: High
Advisory: GHSA-8jq6-w5cg-wm45
CWE: CWE-400
Ecosystem: Packagist
Published: 2020-11-11
Source: https://github.com/advisories/GHSA-8jq6-w5cg-wm45
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <3.15.4

## Details
### Impact
Specially crafted `InventoryTransactionPacket`s sent by malicious clients were able to exploit the behaviour of `InventoryTransaction->findResultItem()` and cause it to take an abnormally long time to execute (causing an apparent server freeze).

The affected code is intended to compact conflicting `InventoryActions` which are in the same `InventoryTransaction` by flattening them into a single action. When multiple pathways to a result existed, the complexity of this flattening became exponential.

The problem was fixed by bailing when ambiguities are detected.

**At the time of writing, this exploit is being used in the wild by attackers to deny service to servers.**

### Patches
Upgrade to 3.15.4 or newer.

### Workarounds
No practical workarounds are possible, short of backporting the fix or implementing checks in a plugin listening to `DataPacketReceiveEvent`.

### References
c368ebb5e74632bc622534b37cd1447b97281e20

### For more information
If you have any questions or comments about this advisory:
* Email us at [team@pmmp.io](mailto:team@pmmp.io)

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-8jq6-w5cg-wm45
