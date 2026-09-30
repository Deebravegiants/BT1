# [?] fix(delayedack): panic on nil reference when err is returned from updateRollapWithStatus (#774)

## Summary
Severity: Unknown
Chain: Dymension
Component: dymensionxyz/dymension
Published: 2024-04-01
Source: https://github.com/dymensionxyz/dymension/commit/8aaca2247210ad31649e150c120ddb9efe45579d
Type: security-commit

## Details
fix(delayedack): panic on nil reference when err is returned from updateRollapWithStatus (#774)

## Patch
### x/delayedack/keeper/rollapp_packet.go
```diff
@@ -107,15 +107,15 @@ func (k *Keeper) UpdateRollappPacketWithStatus(ctx sdk.Context, rollappPacket co
 	// Create a new rollapp packet with the updated status
 	err := k.SetRollappPacket(ctx, rollappPacket)
 	if err != nil {
-		return commontypes.RollappPacket{}, err
+		return rollappPacket, err
 	}
 
 	// Call hook subscribers
 	newKey := commontypes.RollappPacketKey(&rollappPacket)
 	keeperHooks := k.GetHooks()
 	err = keeperHooks.AfterPacketStatusUpdated(ctx, &rollappPacket, string(oldKey), string(newKey))
 	if err != nil {
-		return commontypes.RollappPacket{}, err
+		return rollappPacket, err
 	}
 	return rollappPacket, nil
 }
```
