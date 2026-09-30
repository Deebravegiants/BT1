# [?] fix: query balances with --resolve-denom panics on invalid metadata.Display (#23149)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2025-01-07
Source: https://github.com/cosmos/cosmos-sdk/commit/f77a27432a398fceb0d51595969df5c196bafabf
Type: security-commit

## Details
fix: query balances with --resolve-denom panics on invalid metadata.Display (#23149)

Co-authored-by: Alex | Skip <alex@skip.money>

## Patch
### x/bank/keeper/grpc_query.go
```diff
@@ -65,7 +65,9 @@ func (k BaseKeeper) AllBalances(ctx context.Context, req *types.QueryAllBalances
 		func(key collections.Pair[sdk.AccAddress, string], value math.Int) (sdk.Coin, error) {
 			if req.ResolveDenom {
 				if metadata, ok := k.GetDenomMetaData(ctx, key.K2()); ok {
-					return sdk.NewCoin(metadata.Display, value), nil
+					if err := sdk.ValidateDenom(metadata.Display); err == nil {
+						return sdk.NewCoin(metadata.Display, value), nil
+					}
 				}
 			}
 			return sdk.NewCoin(key.K2(), value), nil
```

### x/bank/keeper/grpc_query_test.go
```diff
@@ -119,11 +119,13 @@ func (suite *KeeperTestSuite) TestQueryAllBalances() {
 	suite.Require().NotNil(res)
 	suite.True(res.Balances.IsZero())
 
-	fooCoins := newFooCoin(50)
 	barCoins := newBarCoin(30)
+	incompleteCoin := newIncompleteMetadataCoin(40)
+	fooCoins := newFooCoin(50)
 	ibcCoins := newIbcCoin(20)
 
-	origCoins := sdk.NewCoins(fooCoins, barCoins, ibcCoins)
+	// NewCoins will sort the Coins, so we prepare in alphabetical order to avoid confusion
+	origCoins := sdk.NewCoins(barCoins, incompleteCoin, fooCoins, ibcCoins)
 
 	suite.mockFundAccount(addr)
 	suite.Require().NoError(testutil.FundAccount(ctx, suite.bankKeeper, addr, origCoins))
@@ -133,10 +135,28 @@ func (suite *KeeperTestSuite) TestQueryAllBalances() {
 	res, err = queryClient.AllBalances(gocontext.Background(), req)
 	suite.Require().NoError(err)
 	suite.Require().NotNil(res)
-	suite.Equal(res.Balances.Len(), 1)
+	suite.Equal(1, res.Balances.Len())
+	suite.Equal(barCoins.Denom, res.Balances[0].Denom)
+	suite.NotNil(res.Pagination.NextKey)
+
+	addIncompleteMetadata(ctx, suite.bankKeeper)
+	suite.T().Log("query second page with nextkey and resolve denom with incomplete metadata")
+	pageReq = &query.PageRequest{
+		Key:        res.Pagination.NextKey,
+		Limit:      1,
+		CountTotal: true,
+	}
+	req = types.NewQueryAllBalancesRequest(addrStr, pageReq, true)
+	testFunc := func() {
+		res, err = queryClient.AllBalances(gocontext.Background(), req)
+	}
+	suite.Require().NotPanics(testFunc, "AllBalances with resolve denom + incomplete metadata")
+	suite.Require().NoError(err)
+	suite.Equal(1, res.Balances.Len())
+	suite.Equal(incompleteCoin.Denom, res.Balances[0].Denom)
 	suite.NotNil(res.Pagination.NextKey)
 
-	suite.T().Log("query second page with nextkey")
+	suite.T().Log("query third page with nextkey")
 	pageReq = &query.PageRequest{
 		Key:        res.Pagination.NextKey,
 		Limit:      1,
@@ -145,34 +165,35 @@ func (suite *KeeperTestSuite) TestQueryAllBalances() {
 	req = types.NewQueryAllBalancesRequest(addrStr, pageReq, false)
 	res, err = queryClient.AllBalances(gocontext.Background(), req)
 	suite.Require().NoError(err)
-	suite.Equal(res.Balances.Len(), 1)
+	suite.Equal(1, res.Balances.Len())
+	suite.Equal(fooCoins.Denom, res.Balances[0].Denom)
 	suite.NotNil(res.Pagination.NextKey)
 
-	pageThree := res.Pagination.NextKey
+	pageFour := res.Pagination.NextKey
 
-	suite.T().Log("query third page with nextkey")
+	suite.T().Log("query fourth page with nextkey")
 	pageReq = &query.PageRequest{
-		Key:        pageThree,
+		Key:        pageFour,
 		Limit:      1,
 		CountTotal: true,
 	}
 	req = types.NewQueryAllBalancesRequest(addrStr, pageReq, false)
 	res, err = queryClient.AllBalances(gocontext.Background(), req)
 	suite.Require().NoError(err)
-	suite.Equal(res.Balances.Len(), 1)
-	suite.Equal(res.Balances[0].Denom, ibcCoins.Denom)
+	suite.Equal(1, res.Balances.Len())
+	suite.Equal(ibcCoins.Denom, res.Balances[0].Denom)
 
-	suite.T().Log("query third page with nextkey and resolve ibc denom")
+	suite.T().Log("query fourth page with nextkey and resolve ibc denom")
 	pageReq = &query.PageRequest{
-		Key:        pageThree,
+		Key:        pageFour,
 		Limit:      1,
 		CountTotal: true,
 	}
 	req = types.NewQueryAllBalancesRequest(addrStr, pageReq, true)
 	res, err = queryClient.AllBalances(gocontext.Background(), req)
 	suite.Require().NoError(err)
-	suite.Equal(res.Balances.Len(), 1)
-	suite.Equal(res.Balances[0].Denom, ibcPath+"/"+ibcBaseDenom)
+	suite.Equal(1, res.Balances.Len())
+	suite.Equal(ibcPath+"/"+ibcBaseDenom, res.Balances[0].Denom)
 	suite.Nil(res.Pagination.NextKey)
 }
 
```

### x/bank/keeper/keeper_test.go
```diff
@@ -41,6 +41,8 @@ const (
 	barDenom            = "bar"
 	ibcPath             = "transfer/channel-0"
 	ibcBaseDenom        = "farboo"
+	incompleteBaseDenom = "incomplete"
+	incompletePath      = "factory/someaddr"
 	metaDataDescription = "IBC Token from %s"
 	initialPower        = int64(100)
 	holder              = "holder"
@@ -83,6 +85,10 @@ func newIbcCoin(amt int64) sdk.Coin {
 	return sdk.NewInt64Coin(getIBCDenom(ibcPath, ibcBaseDenom), amt)
 }
 
+func newIncompleteMetadataCoin(amt int64) sdk.Coin {
+	return sdk.NewInt64Coin(incompletePath+"/"+incompleteBaseDenom, amt)
+}
+
 func getIBCDenom(path, baseDenom string) string {
 	return fmt.Sprintf("%s/%s", "ibc", hex.EncodeToString(getIBCHash(path, baseDenom)))
 }
@@ -109,6 +115,21 @@ func addIBCMetadata(ctx context.Context, k keeper.BaseKeeper) {
 	k.SetDenomMetaData(ctx, metadata)
 }
 
+func addIncompleteMetadata(ctx context.Context, k keeper.BaseKeeper) {
+	metadata := banktypes.Metadata{
+		Description: "Incomplete metadata without display field",
+		DenomUnits: []*banktypes.DenomUnit{
+			{
+				Denom:    incompleteBaseDenom,
+				Exponent: 0,
+			},
+		},
+		Base: incompletePath + "/" + incompleteBaseDenom,
+		// Not setting any Display value
+	}
+	k.SetDenomMetaData(ctx, metadata)
+}
+
 type KeeperTestSuite struct {
 	suite.Suite
 
```
