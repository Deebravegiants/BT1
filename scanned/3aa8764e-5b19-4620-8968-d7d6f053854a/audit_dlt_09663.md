# [?] fix(streamer): panic in pump streamer when spending entire epoch budget (#2076)

## Summary
Severity: Unknown
Chain: Dymension
Component: dymensionxyz/dymension
Published: 2025-10-23
Source: https://github.com/dymensionxyz/dymension/commit/098ecddbae8053e9e6776ca3b1c4f28664d4876c
Type: security-commit

## Details
fix(streamer): panic in pump streamer when spending entire epoch budget (#2076)

fix: panic in pump streamer when spending entire epoch budget

## Patch
### x/streamer/keeper/pump_stream.go
```diff
@@ -433,6 +433,10 @@ func (k Keeper) DistributePumpStreams(ctx sdk.Context, pumpStreams []types.Strea
 			// Skip non-pump streams
 			continue
 		}
+		if len(stream.PumpParams.EpochCoinsLeft) == 0 {
+			// Nothing to pump
+			continue
+		}
 
 		epochBlocks, err := k.EpochBlocks(ctx, stream.DistrEpochIdentifier)
 		if err != nil {
```
