# [?] fix: add error and panic if there is any issue on removing delta sats (#1813)

## Summary
Severity: Unknown
Chain: Babylon
Component: babylonlabs-io/babylon
Published: 2025-10-20
Source: https://github.com/babylonlabs-io/babylon/commit/18f69ed1dddb87c284c1137c2e01c3126863e440
Type: security-commit

## Details
fix: add error and panic if there is any issue on removing delta sats (#1813)

Audit V4-CORE-008

## Patch
### CHANGELOG.md
```diff
@@ -43,6 +43,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
 - [#1764](https://github.com/babylonlabs-io/babylon/pull/1764) Add mergify yaml file for automatic backporting
 - [#1785](https://github.com/babylonlabs-io/babylon/pull/1785) CI reusable to v0.13.5 and golang lint version 2
 - [#1776](https://github.com/babylonlabs-io/babylon/pull/1776) Track baby staked to active validators only
+- [#1813](https://github.com/babylonlabs-io/babylon/pull/1813) Panic if there is an invalid amount of sats in the
+finality provider distribution info
 
 ### Bug fixes
 
```

### x/finality/keeper/power_dist_change.go
```diff
@@ -282,7 +282,9 @@ func (k Keeper) ProcessAllPowerDistUpdateEvents(
 		fpDeltaSats := state.DeltaSatsByFpBtcPk[fpBTCPKHex]
 		// handle delta sats based on new BTC delegations and
 		// unbonded delegations for this finality provider
-		fp.ChangeDeltaSats(fpDeltaSats)
+		if err := fp.ChangeDeltaSats(fpDeltaSats); err != nil {
+			panic(fmt.Sprintf("unable to update delta sats %d fp %s - %s", fpDeltaSats, fpBTCPKHex, err.Error()))
+		}
 		// remove the finality provider entry in fpActiveSats map, so that
 		// after the for loop the rest entries in fpActiveSats belongs to new
 		// finality providers with new BTC delegations
@@ -337,7 +339,9 @@ func (k Keeper) ProcessAllPowerDistUpdateEvents(
 		// update the bonded sats for this finality provider
 		// if had any delta sats during the power distribution change
 		fpDeltaSats := state.DeltaSatsByFpBtcPk[fpBTCPKHex]
-		fpDistInfo.ChangeDeltaSats(fpDeltaSats)
+		if err := fpDistInfo.ChangeDeltaSats(fpDeltaSats); err != nil {
+			panic(fmt.Sprintf("unable to update delta sats %d fp %s - %s", fpDeltaSats, fpBTCPKHex, err.Error()))
+		}
 
 		// add this finality provider to the new cache if it has voting power
 		if fpDistInfo.TotalBondedSat > 0 {
```

### x/finality/types/errors.go
```diff
@@ -27,4 +27,5 @@ var (
 	ErrInvalidPubRandCommit           = errorsmod.Register(ModuleName, 1118, "the public randomness commitment is invalid")
 	ErrInvalidResumeFinality          = errorsmod.Register(ModuleName, 1121, "resume finality proposal message is not valid")
 	ErrFinalityProviderIsDeleted      = errorsmod.Register(ModuleName, 1122, "finality provider is deleted")
+	ErrInvalidSats                    = errorsmod.Register(ModuleName, 1123, "invalid satoshi amount")
 )
```

### x/finality/types/power_table.go
```diff
@@ -242,26 +242,27 @@ func (v *FinalityProviderDistInfo) GetAddress() sdk.AccAddress {
 	return v.Addr
 }
 
-func (v *FinalityProviderDistInfo) ChangeDeltaSats(fpDeltaSats int64) {
+func (v *FinalityProviderDistInfo) ChangeDeltaSats(fpDeltaSats int64) error {
 	switch {
 	case fpDeltaSats > 0:
 		v.AddBondedSats(uint64(fpDeltaSats))
 	case fpDeltaSats < 0:
 		satsToRemove := abs(fpDeltaSats)
-		v.RemoveBondedSats(uint64(satsToRemove))
+		return v.RemoveBondedSats(uint64(satsToRemove))
 	}
+	return nil
 }
 
 func (v *FinalityProviderDistInfo) AddBondedSats(sats uint64) {
 	v.TotalBondedSat += sats
 }
 
-func (v *FinalityProviderDistInfo) RemoveBondedSats(sats uint64) {
-	// safeguard against underflow in total bonded satoshis
+func (v *FinalityProviderDistInfo) RemoveBondedSats(sats uint64) error {
 	if v.TotalBondedSat < sats {
-		sats = v.TotalBondedSat
+		return ErrInvalidSats.Wrapf("removed amount: %d is bigger than the current total bonded: %d", sats, v.TotalBondedSat)
 	}
 	v.TotalBondedSat -= sats
+	return nil
 }
 
 // GetBTCDelPortion returns the portion of a BTC delegation's voting power out of
```

### x/finality/types/power_table_test.go
```diff
@@ -365,6 +365,72 @@ func FuzzSortingDeterminism(f *testing.F) {
 	})
 }
 
+func TestFinalityProviderDistInfoChangeDeltaSats(t *testing.T) {
+	tests := []struct {
+		name         string
+		initialSats  uint64
+		deltaSats    int64
+		expectedSats uint64
+		expErr       error
+	}{
+		{
+			name:         "add positive delta",
+			initialSats:  1000,
+			deltaSats:    500,
+			expectedSats: 1500,
+		},
+		{
+			name:         "remove valid negative delta",
+			initialSats:  1000,
+			deltaSats:    -500,
+			expectedSats: 500,
+		},
+		{
+			name:         "zero delta - no change",
+			initialSats:  1000,
+			deltaSats:    0,
+			expectedSats: 1000,
+		},
+		{
+			name:         "remove all with negative delta",
+			initialSats:  1000,
+			deltaSats:    -1000,
+			expectedSats: 0,
+		},
+		{
+			name:        "negative delta causing underflow",
+			initialSats: 1000,
+			deltaSats:   -1500,
+			expErr:      types.ErrInvalidSats.Wrapf("removed amount: %d is bigger than the current total bonded: %d", 1500, 1000),
+		},
+		{
+			name:        "negative delta on zero balance",
+			initialSats: 0,
+			deltaSats:   -100,
+			expErr:      types.ErrInvalidSats.Wrapf("removed amount: %d is bigger than the current total bonded: %d", 100, 0),
+		},
+	}
+
+	for _, tc := range tests {
+		t.Run(tc.name, func(t *testing.T) {
+			fpDistInfo := &types.FinalityProviderDistInfo{
+				BtcPk:          fpPubKey1,
+				TotalBondedSat: tc.initialSats,
+				Addr:           fpAddr1,
+				Commission:     &validComm,
+			}
+
+			actErr := fpDistInfo.ChangeDeltaSats(tc.deltaSats)
+			if tc.expErr != nil {
+				require.EqualError(t, actErr, tc.expErr.Error())
+				return
+			}
+			require.NoError(t, actErr)
+			require.Equal(t, tc.expectedSats, fpDistInfo.TotalBondedSat)
+		})
+	}
+}
+
 func TestVotingPowerDistCache_Validate(t *testing.T) {
 	t.Parallel()
 	tcs := []struct {
```
