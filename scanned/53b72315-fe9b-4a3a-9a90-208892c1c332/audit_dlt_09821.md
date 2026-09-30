# [?] prevent nil pointer crash

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2020-11-05
Source: https://github.com/harmony-one/harmony/commit/ceaf76e021446dc0bc719230ab44f248582b49fb
Type: security-commit

## Details
prevent nil pointer crash

## Patch
### consensus/quorum/one-node-staked-vote.go
```diff
@@ -173,9 +173,11 @@ func (v *stakedVoteWeight) computeTotalPowerByMask(mask *bls_cosi.Mask) *numeric
 
 	for key, i := range mask.PublicsIndex {
 		if enabled, err := mask.IndexEnabled(i); err == nil && enabled {
-			currentTotal = currentTotal.Add(
-				v.roster.Voters[key].OverallPercent,
-			)
+			if voter, ok := v.roster.Voters[key]; ok {
+				currentTotal = currentTotal.Add(
+					voter.OverallPercent,
+				)
+			}
 		}
 	}
 	return &currentTotal
```
