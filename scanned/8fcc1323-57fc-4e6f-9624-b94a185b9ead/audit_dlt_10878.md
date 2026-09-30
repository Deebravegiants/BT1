# [?] security fix

## Summary
Severity: Unknown
Chain: THORChain
Component: thorchain/thornode
Published: 2019-10-27
Source: https://github.com/thorchain/thornode/commit/77628d8add53917c000723ac739cbad7b81e78a7
Type: security-commit

## Details
security fix

## Patch
### x/swapservice/handler.go
```diff
@@ -716,12 +716,19 @@ func getMsgStakeFromMemo(ctx sdk.Context, memo StakeMemo, txID common.TxID, tx *
 		return nil, errors.Errorf("did not find %s ", asset)
 	}
 
+	runeAddr := tx.Sender
+	assetAddr := memo.GetDestination()
+	if !runeAddr.IsChain(common.BNBChain) {
+		runeAddr = memo.GetDestination()
+		assetAddr = tx.Sender
+	}
+
 	return NewMsgSetStakeData(
 		asset,
 		runeAmount,
 		assetAmount,
-		tx.Sender,
-		memo.GetAssetAddress(),
+		runeAddr,
+		assetAddr,
 		txID,
 		signer,
 	), nil
```

### x/swapservice/memo.go
```diff
@@ -103,7 +103,6 @@ type Memo interface {
 	GetBlockHeight() uint64
 	GetNodeAddress() sdk.AccAddress
 	GetNextPoolAddress() common.Address
-	GetAssetAddress() common.Address
 }
 
 type MemoBase struct {
@@ -125,9 +124,9 @@ type AddMemo struct {
 
 type StakeMemo struct {
 	MemoBase
-	RuneAmount   string
-	AssetAmount  string
-	AssetAddress common.Address
+	RuneAmount  string
+	AssetAmount string
+	Address     common.Address
 }
 
 type WithdrawMemo struct {
@@ -235,8 +234,8 @@ func ParseMemo(memo string) (Memo, error) {
 			}
 		}
 		return StakeMemo{
-			MemoBase:     MemoBase{TxType: txStake, Asset: asset},
-			AssetAddress: addr,
+			MemoBase: MemoBase{TxType: txStake, Asset: asset},
+			Address:  addr,
 		}, nil
 
 	case txWithdraw:
@@ -336,7 +335,6 @@ func (m MemoBase) GetKey() string                     { return "" }
 func (m MemoBase) GetValue() string                   { return "" }
 func (m MemoBase) GetBlockHeight() uint64             { return 0 }
 func (m MemoBase) GetNodeAddress() sdk.AccAddress     { return sdk.AccAddress{} }
-func (m MemoBase) GetAssetAddress() common.Address    { return "" }
 func (m MemoBase) GetNextPoolAddress() common.Address { return "" }
 
 // Transaction Specific Functions
@@ -348,4 +346,4 @@ func (m AdminMemo) GetValue() string                      { return m.Value }
 func (m OutboundMemo) GetBlockHeight() uint64             { return m.BlockHeight }
 func (m BondMemo) GetNodeAddress() sdk.AccAddress         { return m.NodeAddress }
 func (m NextPoolMemo) GetNextPoolAddress() common.Address { return m.NextPoolAddr }
-func (m StakeMemo) GetAssetAddress() common.Address       { return m.AssetAddress }
+func (m StakeMemo) GetDestination() common.Address        { return m.Address }
```

### x/swapservice/memo_test.go
```diff
@@ -122,7 +122,7 @@ func (s *MemoSuite) TestParse(c *C) {
 	c.Assert(err, NotNil)
 	memo, err = ParseMemo("STAKE:BTC.BTC:bc1qwqdg6squsna38e46795at95yu9atm8azzmyvckulcc7kytlcckxswvvzej")
 	c.Assert(err, IsNil)
-	c.Check(memo.GetAssetAddress().String(), Equals, "bc1qwqdg6squsna38e46795at95yu9atm8azzmyvckulcc7kytlcckxswvvzej")
+	c.Check(memo.GetDestination().String(), Equals, "bc1qwqdg6squsna38e46795at95yu9atm8azzmyvckulcc7kytlcckxswvvzej")
 	c.Check(memo.IsType(txStake), Equals, true, Commentf("MEMO: %+v", memo))
 
 	memo, err = ParseMemo("WITHDRAW:RUNE-1BA:25")
```

### x/swapservice/stake.go
```diff
@@ -58,19 +58,18 @@ func stake(ctx sdk.Context, keeper poolStorage, asset common.Asset, stakeRuneAmo
 	if stakeRuneAmount.IsZero() && stakeAssetAmount.IsZero() {
 		return sdk.ZeroUint(), errors.New("both rune and asset is zero")
 	}
+	if runeAddr.IsEmpty() {
+		return sdk.ZeroUint(), errors.New("Rune address cannot be empty")
+	}
+
 	pool := keeper.GetPool(ctx, asset)
 
 	ps, err := keeper.GetPoolStaker(ctx, asset)
 	if nil != err {
 		return sdk.ZeroUint(), errors.Wrap(err, "fail to get pool staker..")
 	}
 
-	addr := assetAddr
-	if addr.IsEmpty() {
-		addr = runeAddr
-	}
-
-	su := ps.GetStakerUnit(addr)
+	su := ps.GetStakerUnit(runeAddr)
 	if su.RuneAddress.IsEmpty() {
 		su.RuneAddress = runeAddr
 	}
```

### x/swapservice/stake_test.go
```diff
@@ -234,7 +234,7 @@ func (StakeSuite) TestStake(c *C) {
 	c.Assert(err, IsNil)
 	c.Check(stakerUnit.IsZero(), Equals, true)
 	// stake btc
-	stakerUnit, err = stake(ctx, ps, common.BTCAsset, sdk.ZeroUint(), sdk.NewUint(100*common.One), common.NoAddress, btcAddress, txId)
+	stakerUnit, err = stake(ctx, ps, common.BTCAsset, sdk.ZeroUint(), sdk.NewUint(100*common.One), bnbAddress, btcAddress, txId)
 	c.Assert(err, IsNil)
 	c.Check(stakerUnit.IsZero(), Equals, false)
 	p = ps.GetPool(ctx, common.BTCAsset)
```

### x/swapservice/types/msg_stake.go
```diff
@@ -46,14 +46,14 @@ func (msg MsgSetStakeData) ValidateBasic() sdk.Error {
 	if msg.RequestTxHash.IsEmpty() {
 		return sdk.ErrUnknownRequest("request tx hash cannot be empty")
 	}
+	if msg.RuneAddress.IsEmpty() {
+		return sdk.ErrUnknownRequest("rune address cannot be empty")
+	}
 	if !common.IsBNBChain(msg.Asset.Chain) {
 		if msg.AssetAddress.IsEmpty() {
 			return sdk.ErrUnknownRequest("asset address cannot be empty")
 		}
-	} else {
-		if msg.RuneAddress.IsEmpty() {
-			return sdk.ErrUnknownRequest("rune address cannot be empty")
-		}
+
 	}
 	return nil
 }
```

### x/swapservice/types/type_pool_staker.go
```diff
@@ -82,7 +82,7 @@ func (ps PoolStaker) String() string {
 
 func (ps *PoolStaker) GetStakerUnit(addr common.Address) StakerUnit {
 	for _, item := range ps.Stakers {
-		if item.RuneAddress == addr || item.AssetAddress == addr {
+		if item.RuneAddress == addr {
 			return item
 		}
 	}
```
