# [?] fixed map nondeterminism (#1281)

## Summary
Severity: Unknown
Chain: Stride
Component: Stride-Labs/stride
Published: 2024-08-30
Source: https://github.com/Stride-Labs/stride/commit/e40a694f29dc20bb773fb8df66f328a45d0fbe62
Type: security-commit

## Details
fixed map nondeterminism (#1281)

## Context
Looping through maps is nondeteministic in go. None of the examples in this PR should actually be able to cause consensus breaking changes, but it's better to play it safe and avoid future footguns.

## Patch
### cmd/strided/config_defaults.go
```diff
@@ -9,6 +9,8 @@ import (
 
 	tmcli "github.com/cometbft/cometbft/libs/cli"
 	"github.com/cosmos/cosmos-sdk/server"
+
+	"github.com/Stride-Labs/stride/v24/utils"
 )
 
 /*
@@ -216,7 +218,8 @@ func OverwriteWithCustomConfig(configFilePath string, sectionKeyValues []Section
 			currentSection = line[1 : len(line)-1]
 		} else if configMap[currentSection] != nil {
 			// If the line is in a section that needs to be overwritten, check each key
-			for key, value := range configMap[currentSection] {
+			for _, key := range utils.StringMapKeys(configMap[currentSection]) {
+				value := configMap[currentSection][key]
 				// Split the line into key and value parts
 				parts := strings.SplitN(line, "=", 2)
 				if len(parts) != 2 {
```

### utils/utils.go
```diff
@@ -68,6 +68,15 @@ func Int32MapKeys[V any](m map[int32]V) []int32 {
 	return keys
 }
 
+func Uint64MapKeys[V any](m map[uint64]V) []uint64 {
+	keys := make([]uint64, 0, len(m))
+	for k := range m {
+		keys = append(keys, k)
+	}
+	sort.Slice(keys, func(i, j int) bool { return keys[i] < keys[j] })
+	return keys
+}
+
 //==============================  ADDRESS VERIFICATION UTILS  ================================
 // ref: https://github.com/cosmos/cosmos-sdk/blob/b75c2ebcfab1a6b535723f1ac2889a2fc2509520/types/address.go#L177
 
```

### x/stakeibc/keeper/unbonding.go
```diff
@@ -140,7 +140,8 @@ func (k Keeper) RefreshUnbondingNativeTokenAmounts(
 ) (refreshedHostZoneUnbondings map[uint64]recordstypes.HostZoneUnbonding, err error) {
 	// Refresh the amount for all records in status UNBONDING_QUEUE
 	// We don't want to refresh the failed unbonding records
-	for epochNumber, hostZoneUnbondingRecord := range hostZoneUnbondings {
+	for _, epochNumber := range utils.Uint64MapKeys(hostZoneUnbondings) {
+		hostZoneUnbondingRecord := hostZoneUnbondings[epochNumber]
 		if hostZoneUnbondingRecord.Status != recordstypes.HostZoneUnbonding_UNBONDING_QUEUE {
 			continue
 		}
@@ -451,7 +452,8 @@ func (k Keeper) UnbondFromHostZone(ctx sdk.Context, hostZone types.HostZone) (er
 	}
 
 	// Update the epoch unbonding record status and number of undelegation ICAs
-	for epochNumber, hostZoneUnbonding := range epochNumbersToHostZoneUnbondings {
+	for _, epochNumber := range utils.Uint64MapKeys(epochNumbersToHostZoneUnbondings) {
+		hostZoneUnbonding := epochNumbersToHostZoneUnbondings[epochNumber]
 		hostZoneUnbonding.Status = recordstypes.HostZoneUnbonding_UNBONDING_IN_PROGRESS
 		hostZoneUnbonding.UndelegationTxsInProgress += numTxsSubmitted
 		err := k.RecordsKeeper.SetHostZoneUnbondingRecord(ctx, epochNumber, hostZone.ChainId, hostZoneUnbonding)
```
