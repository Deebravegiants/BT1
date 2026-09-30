# [?] Merge pull request from GHSA-4j93-fm92-rp4m

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2024-02-19
Source: https://github.com/cosmos/cosmos-sdk/commit/7dbed2fc0c3ed7c285645e21cb1037d8810372ae
Type: security-commit

## Details
Merge pull request from GHSA-4j93-fm92-rp4m

* fix(x/auth/vesting): Add `BlockedAddr` check in `CreatePeriodicVestingAccount`

* updates

## Patch
### CHANGELOG.md
```diff
@@ -50,6 +50,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 
 ### Bug Fixes
 
+* (x/auth/vesting) [GHSA-4j93-fm92-rp4m](#bug-fixes) Add `BlockedAddr` check in `CreatePeriodicVestingAccount`.
 * (baseapp) [#19338](https://github.com/cosmos/cosmos-sdk/pull/19338) Set HeaderInfo in context when calling `setState`.
 * (baseapp): [#19200](https://github.com/cosmos/cosmos-sdk/pull/19200) Ensure that sdk side ve math matches cometbft.
 * [#19106](https://github.com/cosmos/cosmos-sdk/pull/19106) Allow empty public keys when setting signatures. Public keys aren't needed for every transaction.
```

### RELEASE_NOTES.md
```diff
@@ -11,9 +11,10 @@ Notably, we added and fixed the following:
 
 * Adds in-place testnet CLI command for creating testnets from local state (kudos to @czarcas7ic)
 * Multiple fixes in baseapp, with fixes in `DefaultProposalHandler` and vote extensions
-* <>
+* Add a missed check in `x/auth/vesting`: [GHSA-4j93-fm92-rp4m](https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-4j93-fm92-rp4m)
 
-We recommended to upgrade to this patch release as soon as possible.
+We recommended to upgrade to this patch release as soon as possible.  
+When upgrading from <= v0.50.3, please ensure that 2/3 of the validator power upgrade to v0.50.4.
 
 ## 📝 Changelog
 
```

### x/auth/vesting/msg_server.go
```diff
@@ -183,6 +183,10 @@ func (s msgServer) CreatePeriodicVestingAccount(goCtx context.Context, msg *type
 		totalCoins = totalCoins.Add(period.Amount...)
 	}
 
+	if s.BankKeeper.BlockedAddr(to) {
+		return nil, errorsmod.Wrapf(sdkerrors.ErrUnauthorized, "%s is not allowed to receive funds", msg.ToAddress)
+	}
+
 	ctx := sdk.UnwrapSDKContext(goCtx)
 	if acc := s.AccountKeeper.GetAccount(ctx, to); acc != nil {
 		return nil, errorsmod.Wrapf(sdkerrors.ErrInvalidRequest, "account %s already exists", msg.ToAddress)
```

### x/auth/vesting/msg_server_test.go
```diff
@@ -136,6 +136,21 @@ func (s *VestingTestSuite) TestCreateVestingAccount() {
 			expErr:    true,
 			expErrMsg: "already exists",
 		},
+		"create for blocked account": {
+			preRun: func() {
+				s.bankKeeper.EXPECT().IsSendEnabledCoins(gomock.Any(), fooCoin).Return(nil)
+				s.bankKeeper.EXPECT().BlockedAddr(to1Addr).Return(true)
+			},
+			input: vestingtypes.NewMsgCreateVestingAccount(
+				fromAddr,
+				to1Addr,
+				sdk.Coins{fooCoin},
+				time.Now().Unix(),
+				true,
+			),
+			expErr:    true,
+			expErrMsg: "not allowed to receive funds",
+		},
 		"create a valid delayed vesting account": {
 			preRun: func() {
 				s.bankKeeper.EXPECT().IsSendEnabledCoins(gomock.Any(), fooCoin).Return(nil)
@@ -235,6 +250,22 @@ func (s *VestingTestSuite) TestCreatePermanentLockedAccount() {
 			expErr:    true,
 			expErrMsg: "already exists",
 		},
+		"create for blocked account": {
+			preRun: func() {
+				toAcc := s.accountKeeper.NewAccountWithAddress(s.ctx, to1Addr)
+				s.bankKeeper.EXPECT().IsSendEnabledCoins(gomock.Any(), fooCoin).Return(nil)
+				s.bankKeeper.EXPECT().BlockedAddr(to1Addr).Return(true)
+				s.accountKeeper.SetAccount(s.ctx, toAcc)
+			},
+			input: vestingtypes.NewMsgCreatePermanentLockedAccount(
+				fromAddr,
+				to1Addr,
+				sdk.Coins{fooCoin},
+			),
+			expErr:    true,
+			expErrMsg: "not allowed to receive funds",
+		},
+
 		"create a valid permanent locked account": {
 			preRun: func() {
 				s.bankKeeper.EXPECT().IsSendEnabledCoins(gomock.Any(), fooCoin).Return(nil)
@@ -359,6 +390,7 @@ func (s *VestingTestSuite) TestCreatePeriodicVestingAccount() {
 		{
 			name: "create for existing account",
 			preRun: func() {
+				s.bankKeeper.EXPECT().BlockedAddr(to1Addr).Return(false)
 				toAcc := s.accountKeeper.NewAccountWithAddress(s.ctx, to1Addr)
 				s.accountKeeper.SetAccount(s.ctx, toAcc)
 			},
@@ -376,10 +408,34 @@ func (s *VestingTestSuite) TestCreatePeriodicVestingAccount() {
 			expErr:    true,
 			expErrMsg: "already exists",
 		},
+		{
+			name: "create for blocked address",
+			preRun: func() {
+				s.bankKeeper.EXPECT().BlockedAddr(to2Addr).Return(true)
+			},
+			input: vestingtypes.NewMsgCreatePeriodicVestingAccount(
+				fromAddr,
+				to2Addr,
+				time.Now().Unix(),
+				[]vestingtypes.Period{
+					{
+						Length: 10,
+						Amount: sdk.NewCoins(periodCoin),
+					},
+					{
+						Length: 20,
+						Amount: sdk.NewCoins(fooCoin),
+					},
+				},
+			),
+			expErr:    true,
+			expErrMsg: "not allowed to receive funds",
+		},
 		{
 			name: "create a valid periodic vesting account",
 			preRun: func() {
 				s.bankKeeper.EXPECT().IsSendEnabledCoins(gomock.Any(), periodCoin.Add(fooCoin)).Return(nil)
+				s.bankKeeper.EXPECT().BlockedAddr(to2Addr).Return(false)
 				s.bankKeeper.EXPECT().SendCoins(gomock.Any(), fromAddr, to2Addr, gomock.Any()).Return(nil)
 			},
 			input: vestingtypes.NewMsgCreatePeriodicVestingAccount(
```
