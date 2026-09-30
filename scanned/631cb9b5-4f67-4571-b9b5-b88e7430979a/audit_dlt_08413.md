# [?] fix(x/auth/vesting): panic on overflowing & negative EndTimes for PeriodicVestingAccount (#16733)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2023-06-28
Source: https://github.com/cosmos/cosmos-sdk/commit/d90abbea5761c2fc348ca8690a8e5fef27f5eea9
Type: security-commit

## Details
fix(x/auth/vesting): panic on overflowing & negative EndTimes for PeriodicVestingAccount (#16733)

## Patch
### CHANGELOG.md
```diff
@@ -69,6 +69,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 
 ### Bug Fixes
 
+* (x/auth/vesting) [#16733](https://github.com/cosmos/cosmos-sdk/pull/16733) panic on overflowing and negative EndTimes when creating a PeriodicVestingAccount
 * [#16547](https://github.com/cosmos/cosmos-sdk/pull/16547) Ensure a transaction's gas limit cannot exceed the block gas limit.
 * (x/auth/types) [#16554](https://github.com/cosmos/cosmos-sdk/pull/16554) `ModuleAccount.Validate` now reports a nil `.BaseAccount` instead of panicking.
 * (baseapp) [#16613](https://github.com/cosmos/cosmos-sdk/pull/16613) Ensure each message in a transaction has a registered handler, otherwise `CheckTx` will fail.
```

### x/auth/vesting/msg_server.go
```diff
@@ -186,6 +186,11 @@ func (s msgServer) CreatePeriodicVestingAccount(goCtx context.Context, msg *type
 	baseAccount = s.AccountKeeper.NewAccount(ctx, baseAccount).(*authtypes.BaseAccount)
 	vestingAccount := types.NewPeriodicVestingAccount(baseAccount, totalCoins.Sort(), msg.StartTime, msg.VestingPeriods)
 
+	// Enforce and sanity check that we don't have any negative endTime.
+	if bva := vestingAccount.BaseVestingAccount; bva != nil && bva.EndTime < 0 {
+		return nil, errorsmod.Wrapf(sdkerrors.ErrInvalidRequest, "cumulative endtime is negative")
+	}
+
 	s.AccountKeeper.SetAccount(ctx, vestingAccount)
 
 	defer func() {
```

### x/auth/vesting/types/vesting_account.go
```diff
@@ -2,6 +2,7 @@ package types
 
 import (
 	"errors"
+	"fmt"
 	"time"
 
 	"cosmossdk.io/math"
@@ -259,9 +260,15 @@ func NewPeriodicVestingAccountRaw(bva *BaseVestingAccount, startTime int64, peri
 // NewPeriodicVestingAccount returns a new PeriodicVestingAccount
 func NewPeriodicVestingAccount(baseAcc *authtypes.BaseAccount, originalVesting sdk.Coins, startTime int64, periods Periods) *PeriodicVestingAccount {
 	endTime := startTime
-	for _, p := range periods {
+	for i, p := range periods {
+		if p.Length < 0 {
+			panic(fmt.Sprintf("period #%d has a negative length: %d", i, p.Length))
+		}
 		endTime += p.Length
 	}
+	if endTime < 0 || endTime < startTime {
+		panic("cumulative endTime overflowed, and/or is less than startTime")
+	}
 	baseVestingAcc := &BaseVestingAccount{
 		BaseAccount:     baseAcc,
 		OriginalVesting: originalVesting,
```

### x/auth/vesting/types/vesting_account_test.go
```diff
@@ -397,6 +397,67 @@ func TestGetVestedCoinsPeriodicVestingAcc(t *testing.T) {
 	require.Equal(t, origCoins, vestedCoins)
 }
 
+func TestOverflowAndNegativeVestedCoinsPeriods(t *testing.T) {
+	now := tmtime.Now()
+	tests := []struct {
+		name      string
+		periods   []types.Period
+		wantPanic string
+	}{
+		{
+			"negative .Length",
+			types.Periods{
+				types.Period{Length: -1, Amount: sdk.Coins{sdk.NewInt64Coin(feeDenom, 500), sdk.NewInt64Coin(stakeDenom, 50)}},
+				types.Period{Length: 6 * 60 * 60, Amount: sdk.Coins{sdk.NewInt64Coin(feeDenom, 250), sdk.NewInt64Coin(stakeDenom, 25)}},
+			},
+			"period #0 has a negative length: -1",
+		},
+		{
+			"overflow after .Length additions",
+			types.Periods{
+				types.Period{Length: 9223372036854775108, Amount: sdk.Coins{sdk.NewInt64Coin(feeDenom, 500), sdk.NewInt64Coin(stakeDenom, 50)}},
+				types.Period{Length: 6 * 60 * 60, Amount: sdk.Coins{sdk.NewInt64Coin(feeDenom, 250), sdk.NewInt64Coin(stakeDenom, 25)}},
+			},
+			"cumulative endTime overflowed, and/or is less than startTime",
+		},
+		{
+			"good periods that are not negative nor overflow",
+			types.Periods{
+				types.Period{Length: now.Unix() - 1000, Amount: sdk.Coins{sdk.NewInt64Coin(feeDenom, 500), sdk.NewInt64Coin(stakeDenom, 50)}},
+				types.Period{Length: 60, Amount: sdk.Coins{sdk.NewInt64Coin(feeDenom, 250), sdk.NewInt64Coin(stakeDenom, 25)}},
+			},
+			"",
+		},
+	}
+
+	for _, tt := range tests {
+		t.Run(tt.name, func(t *testing.T) {
+			bacc, origCoins := initBaseAccount()
+			defer func() {
+				r := recover()
+				if r == nil {
+					if tt.wantPanic != "" {
+						t.Fatalf("expected a panic with substring: %q", tt.wantPanic)
+					}
+					return
+				}
+
+				// Otherwise ensure we match the panic substring.
+				require.Contains(t, r, tt.wantPanic)
+			}()
+
+			pva := types.NewPeriodicVestingAccount(bacc, origCoins, now.Unix(), tt.periods)
+			if pva == nil {
+				return
+			}
+
+			if pbva := pva.BaseVestingAccount; pbva.EndTime < 0 {
+				t.Fatalf("Unfortunately we still have negative .EndTime :-(: %d", pbva.EndTime)
+			}
+		})
+	}
+}
+
 func TestGetVestingCoinsPeriodicVestingAcc(t *testing.T) {
 	now := tmtime.Now()
 	endTime := now.Add(24 * time.Hour)
```
