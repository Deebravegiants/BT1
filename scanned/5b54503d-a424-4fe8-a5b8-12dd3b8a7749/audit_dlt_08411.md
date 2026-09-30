# [?] Merge pull request from GHSA-j2cr-jc39-wpx5

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2023-06-29
Source: https://github.com/cosmos/cosmos-sdk/commit/2bbc3a1c61af5335caf4358d49c3f7479d801f60
Type: security-commit

## Details
Merge pull request from GHSA-j2cr-jc39-wpx5

## Patch
### x/auth/vesting/msg_server.go
```diff
@@ -170,6 +170,10 @@ func (s msgServer) CreatePeriodicVestingAccount(goCtx context.Context, msg *type
 			return nil, errorsmod.Wrapf(sdkerrors.ErrInvalidRequest, "invalid period length of %d in period %d, length must be greater than 0", period.Length, i)
 		}
 
+		if err := validateAmount(period.Amount); err != nil {
+			return nil, err
+		}
+
 		totalCoins = totalCoins.Add(period.Amount...)
 	}
 
```

### x/auth/vesting/msg_server_test.go
```diff
@@ -9,6 +9,7 @@ import (
 	"github.com/golang/mock/gomock"
 	"github.com/stretchr/testify/suite"
 
+	"cosmossdk.io/math"
 	storetypes "cosmossdk.io/store/types"
 
 	"github.com/cosmos/cosmos-sdk/runtime"
@@ -96,7 +97,18 @@ func (s *VestingTestSuite) TestCreateVestingAccount() {
 			expErr:    true,
 			expErrMsg: "invalid 'to' address",
 		},
-		"": {
+		"invalid coins": {
+			input: vestingtypes.NewMsgCreateVestingAccount(
+				fromAddr,
+				to1Addr,
+				sdk.Coins{sdk.Coin{Denom: "stake", Amount: math.NewInt(-1)}},
+				time.Now().Unix(),
+				true,
+			),
+			expErr:    true,
+			expErrMsg: "-1stake: invalid coins",
+		},
+		"invalid end time": {
 			input: vestingtypes.NewMsgCreateVestingAccount(
 				fromAddr,
 				to1Addr,
@@ -199,6 +211,15 @@ func (s *VestingTestSuite) TestCreatePermanentLockedAccount() {
 			expErr:    true,
 			expErrMsg: "invalid 'to' address",
 		},
+		"invalid coins": {
+			input: vestingtypes.NewMsgCreatePermanentLockedAccount(
+				fromAddr,
+				to1Addr,
+				sdk.Coins{sdk.Coin{Denom: "stake", Amount: math.NewInt(-1)}},
+			),
+			expErr:    true,
+			expErrMsg: "-1stake: invalid coins",
+		},
 		"create for existing account": {
 			preRun: func() {
 				toAcc := s.accountKeeper.NewAccountWithAddress(s.ctx, to1Addr)
@@ -319,6 +340,22 @@ func (s *VestingTestSuite) TestCreatePeriodicVestingAccount() {
 			expErr:    true,
 			expErrMsg: "invalid period",
 		},
+		{
+			name: "invalid coins",
+			input: vestingtypes.NewMsgCreatePeriodicVestingAccount(
+				fromAddr,
+				to1Addr,
+				time.Now().Unix(),
+				[]vestingtypes.Period{
+					{
+						Length: 1,
+						Amount: sdk.Coins{sdk.Coin{Denom: "stake", Amount: math.NewInt(-1)}},
+					},
+				},
+			),
+			expErr:    true,
+			expErrMsg: "-1stake: invalid coins",
+		},
 		{
 			name: "create for existing account",
 			preRun: func() {
```
