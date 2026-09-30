# [?] Fix: division by zero panic in assignment (#340)

## Summary
Severity: Unknown
Chain: EigenDA
Component: Layr-Labs/eigenda
Published: 2024-03-15
Source: https://github.com/Layr-Labs/eigenda/commit/28e3c4b239d10e3bb6d3304ccfde6ad2fed78952
Type: security-commit

## Details
Fix: division by zero panic in assignment (#340)

## Patch
### core/assignment.go
```diff
@@ -105,6 +105,9 @@ func (c *StdAssignmentCoordinator) GetAssignments(state *OperatorState, blobLeng
 
 		gammaChunkLength := big.NewInt(int64(info.ChunkLength) * int64((info.QuorumThreshold - info.AdversaryThreshold)))
 		denom := new(big.Int).Mul(gammaChunkLength, totalStakes)
+		if denom.Cmp(big.NewInt(0)) == 0 {
+			return nil, AssignmentInfo{}, fmt.Errorf("gammaChunkLength %d and total stake in quorum %d must be greater than 0", gammaChunkLength, totalStakes)
+		}
 		m := roundUpDivideBig(num, denom)
 
 		numChunks += uint(m.Uint64())
```
