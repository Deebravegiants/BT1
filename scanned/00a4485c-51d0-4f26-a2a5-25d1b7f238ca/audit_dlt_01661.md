# [?] [CL Incentives] Key incentive records by owner address to prevent DoS/trolling (#4581)

## Summary
Severity: Unknown
Chain: Osmosis
Component: osmosis-labs/osmosis
Published: 2023-03-15
Source: https://github.com/osmosis-labs/osmosis/commit/f85d4ea4071ecc9de2ce2a0a6a9b8e8197b11122
Type: security-commit

## Details
[CL Incentives] Key incentive records by owner address to prevent DoS/trolling (#4581)

* implement core logic and clean up tests

* minor comment cleanup

* fix conflicts

* lint

* remove duplicate code after merge

## Patch
### x/concentrated-liquidity/incentives.go
```diff
@@ -234,7 +234,7 @@ func calcAccruedIncentivesForAccum(ctx sdk.Context, accumUptime time.Duration, q
 // setIncentiveRecords sets the passed in incentive records in state
 func (k Keeper) setIncentiveRecord(ctx sdk.Context, incentiveRecord types.IncentiveRecord) {
 	store := ctx.KVStore(k.storeKey)
-	key := types.KeyIncentiveRecord(incentiveRecord.PoolId, incentiveRecord.IncentiveDenom, incentiveRecord.MinUptime)
+	key := types.KeyIncentiveRecord(incentiveRecord.PoolId, incentiveRecord.IncentiveDenom, incentiveRecord.MinUptime, incentiveRecord.IncentiveCreator)
 	incentiveRecordBody := types.IncentiveRecordBody{
 		RemainingAmount: incentiveRecord.RemainingAmount,
 		EmissionRate:    incentiveRecord.EmissionRate,
@@ -252,27 +252,28 @@ func (k Keeper) setMultipleIncentiveRecords(ctx sdk.Context, incentiveRecords []
 }
 
 // GetIncentiveRecord gets the incentive record corresponding to the passed in values from store
-func (k Keeper) GetIncentiveRecord(ctx sdk.Context, poolId uint64, denom string, minUptime time.Duration) (types.IncentiveRecord, error) {
+func (k Keeper) GetIncentiveRecord(ctx sdk.Context, poolId uint64, denom string, minUptime time.Duration, incentiveCreator sdk.AccAddress) (types.IncentiveRecord, error) {
 	store := ctx.KVStore(k.storeKey)
 	incentiveBodyStruct := types.IncentiveRecordBody{}
-	key := types.KeyIncentiveRecord(poolId, denom, minUptime)
+	key := types.KeyIncentiveRecord(poolId, denom, minUptime, incentiveCreator)
 
 	found, err := osmoutils.Get(store, key, &incentiveBodyStruct)
 	if err != nil {
 		return types.IncentiveRecord{}, err
 	}
 
 	if !found {
-		return types.IncentiveRecord{}, types.IncentiveRecordNotFoundError{PoolId: poolId, IncentiveDenom: denom, MinUptime: minUptime}
+		return types.IncentiveRecord{}, types.IncentiveRecordNotFoundError{PoolId: poolId, IncentiveDenom: denom, MinUptime: minUptime, IncentiveCreatorStr: incentiveCreator.String()}
 	}
 
 	return types.IncentiveRecord{
-		PoolId:          poolId,
-		IncentiveDenom:  denom,
-		MinUptime:       minUptime,
-		RemainingAmount: incentiveBodyStruct.RemainingAmount,
-		EmissionRate:    incentiveBodyStruct.EmissionRate,
-		StartTime:       incentiveBodyStruct.StartTime,
+		PoolId:           poolId,
+		IncentiveDenom:   denom,
+		IncentiveCreator: incentiveCreator,
+		MinUptime:        minUptime,
+		RemainingAmount:  incentiveBodyStruct.RemainingAmount,
+		EmissionRate:     incentiveBodyStruct.EmissionRate,
+		StartTime:        incentiveBodyStruct.StartTime,
 	}, nil
 }
 
@@ -582,12 +583,13 @@ func (k Keeper) createIncentive(ctx sdk.Context, poolId uint64, sender sdk.AccAd
 
 	// Set up incentive record to put in state
 	incentiveRecord := types.IncentiveRecord{
-		PoolId:          poolId,
-		IncentiveDenom:  incentiveDenom,
-		RemainingAmount: incentiveAmount.ToDec(),
-		EmissionRate:    emissionRate,
-		StartTime:       startTime,
-		MinUptime:       minUptime,
+		PoolId:           poolId,
+		IncentiveDenom:   incentiveDenom,
+		IncentiveCreator: sender,
+		RemainingAmount:  incentiveAmount.ToDec(),
+		EmissionRate:     emissionRate,
+		StartTime:        startTime,
+		MinUptime:        minUptime,
 	}
 
 	// Set incentive record in state
```

### x/concentrated-liquidity/incentives_test.go
```diff
@@ -22,6 +22,7 @@ var (
 	testAddressOne   = sdk.AccAddress([]byte("addr1_______________"))
 	testAddressTwo   = sdk.AccAddress([]byte("addr2_______________"))
 	testAddressThree = sdk.AccAddress([]byte("addr3_______________"))
+	testAddressFour  = sdk.AccAddress([]byte("addr4_______________"))
 
 	testAccumOne = "testAccumOne"
 
@@ -48,39 +49,43 @@ var (
 	testUptimeFour  = types.SupportedUptimes[3]
 
 	incentiveRecordOne = types.IncentiveRecord{
-		PoolId:          validPoolId,
-		IncentiveDenom:  testDenomOne,
-		RemainingAmount: defaultIncentiveAmount,
-		EmissionRate:    testEmissionOne,
-		StartTime:       defaultStartTime,
-		MinUptime:       testUptimeOne,
+		PoolId:           validPoolId,
+		IncentiveDenom:   testDenomOne,
+		IncentiveCreator: testAddressOne,
+		RemainingAmount:  defaultIncentiveAmount,
+		EmissionRate:     testEmissionOne,
+		StartTime:        defaultStartTime,
+		MinUptime:        testUptimeOne,
 	}
 
 	incentiveRecordTwo = types.IncentiveRecord{
-		PoolId:          validPoolId,
-		IncentiveDenom:  testDenomTwo,
-		RemainingAmount: defaultIncentiveAmount,
-		EmissionRate:    testEmissionTwo,
-		StartTime:       defaultStartTime,
-		MinUptime:       testUptimeTwo,
+		PoolId:           validPoolId,
+		IncentiveDenom:   testDenomTwo,
+		IncentiveCreator: testAddressTwo,
+		RemainingAmount:  defaultIncentiveAmount,
+		EmissionRate:     testEmissionTwo,
+		StartTime:        defaultStartTime,
+		MinUptime:        testUptimeTwo,
 	}
 
 	incentiveRecordThree = types.IncentiveRecord{
-		PoolId:          validPoolId,
-		IncentiveDenom:  testDenomThree,
-		RemainingAmount: defaultIncentiveAmount,
-		EmissionRate:    testEmissionThree,
-		StartTime:       defaultStartTime,
-		MinUptime:       testUptimeThree,
+		PoolId:           validPoolId,
+		IncentiveDenom:   testDenomThree,
+		IncentiveCreator: testAddressThree,
+		RemainingAmount:  defaultIncentiveAmount,
+		EmissionRate:     testEmissionThree,
+		StartTime:        defaultStartTime,
+		MinUptime:        testUptimeThree,
 	}
 
 	incentiveRecordFour = types.IncentiveRecord{
-		PoolId:          validPoolId,
-		IncentiveDenom:  testDenomFour,
-		RemainingAmount: defaultIncentiveAmount,
-		EmissionRate:    testEmissionFour,
-		StartTime:       defaultStartTime,
-		MinUptime:       testUptimeFour,
+		PoolId:           validPoolId,
+		IncentiveDenom:   testDenomFour,
+		IncentiveCreator: testAddressFour,
+		RemainingAmount:  defaultIncentiveAmount,
+		EmissionRate:     testEmissionFour,
+		StartTime:        defaultStartTime,
+		MinUptime:        testUptimeFour,
 	}
 
 	testQualifyingDepositsOne   = sdk.NewInt(50)
@@ -847,25 +852,25 @@ func (s *KeeperTestSuite) TestIncentiveRecordsSetAndGet() {
 
 	// Ensure setting and getting a single record works with single Get and GetAll
 	clKeeper.SetIncentiveRecord(s.Ctx, incentiveRecordOne)
-	poolOneRecord, err := clKeeper.GetIncentiveRecord(s.Ctx, clPoolOne.GetId(), incentiveRecordOne.IncentiveDenom, incentiveRecordOne.MinUptime)
+	poolOneRecord, err := clKeeper.GetIncentiveRecord(s.Ctx, clPoolOne.GetId(), incentiveRecordOne.IncentiveDenom, incentiveRecordOne.MinUptime, incentiveRecordOne.IncentiveCreator)
 	s.Require().NoError(err)
 	s.Require().Equal(incentiveRecordOne, poolOneRecord)
 	allRecordsPoolOne, err := clKeeper.GetAllIncentiveRecordsForPool(s.Ctx, clPoolOne.GetId())
 	s.Require().NoError(err)
 	s.Require().Equal([]types.IncentiveRecord{incentiveRecordOne}, allRecordsPoolOne)
 
 	// Ensure records for other pool remain unchanged
-	poolTwoRecord, err := clKeeper.GetIncentiveRecord(s.Ctx, clPoolTwo.GetId(), incentiveRecordOne.IncentiveDenom, incentiveRecordOne.MinUptime)
+	poolTwoRecord, err := clKeeper.GetIncentiveRecord(s.Ctx, clPoolTwo.GetId(), incentiveRecordOne.IncentiveDenom, incentiveRecordOne.MinUptime, incentiveRecordOne.IncentiveCreator)
 	s.Require().Error(err)
-	s.Require().ErrorIs(err, types.IncentiveRecordNotFoundError{PoolId: clPoolTwo.GetId(), IncentiveDenom: incentiveRecordOne.IncentiveDenom, MinUptime: incentiveRecordOne.MinUptime})
+	s.Require().ErrorIs(err, types.IncentiveRecordNotFoundError{PoolId: clPoolTwo.GetId(), IncentiveDenom: incentiveRecordOne.IncentiveDenom, MinUptime: incentiveRecordOne.MinUptime, IncentiveCreatorStr: incentiveRecordOne.IncentiveCreator.String()})
 	s.Require().Equal(types.IncentiveRecord{}, poolTwoRecord)
 	allRecordsPoolTwo, err := clKeeper.GetAllIncentiveRecordsForPool(s.Ctx, clPoolTwo.GetId())
 	s.Require().NoError(err)
 	s.Require().Equal(emptyIncentiveRecords, allRecordsPoolTwo)
 
 	// Ensure directly setting additional records don't overwrite previous ones
 	clKeeper.SetIncentiveRecord(s.Ctx, incentiveRecordTwo)
-	poolOneRecord, err = clKeeper.GetIncentiveRecord(s.Ctx, clPoolOne.GetId(), incentiveRecordTwo.IncentiveDenom, incentiveRecordTwo.MinUptime)
+	poolOneRecord, err = clKeeper.GetIncentiveRecord(s.Ctx, clPoolOne.GetId(), incentiveRecordTwo.IncentiveDenom, incentiveRecordTwo.MinUptime, incentiveRecordTwo.IncentiveCreator)
 	s.Require().NoError(err)
 	s.Require().Equal(incentiveRecordTwo, poolOneRecord)
 	allRecordsPoolOne, err = clKeeper.GetAllIncentiveRecordsForPool(s.Ctx, clPoolOne.GetId())
@@ -2734,7 +2739,7 @@ func (s *KeeperTestSuite) TestCreateIncentive() {
 	tests := map[string]testCreateIncentive{
 		"valid incentive record": {
 			poolId: defaultPoolId,
-			sender: s.TestAccs[0],
+			sender: incentiveRecordOne.IncentiveCreator,
 			senderBalance: sdk.NewCoins(
 				sdk.NewCoin(
 					incentiveRecordOne.IncentiveDenom,
@@ -2745,7 +2750,7 @@ func (s *KeeperTestSuite) TestCreateIncentive() {
 		},
 		"record with different denom, emission rate, and min uptime": {
 			poolId: defaultPoolId,
-			sender: s.TestAccs[0],
+			sender: incentiveRecordTwo.IncentiveCreator,
 			senderBalance: sdk.NewCoins(
 				sdk.NewCoin(
 					incentiveRecordTwo.IncentiveDenom,
@@ -2756,7 +2761,7 @@ func (s *KeeperTestSuite) TestCreateIncentive() {
 		},
 		"record with different start time": {
 			poolId: defaultPoolId,
-			sender: s.TestAccs[0],
+			sender: incentiveRecordOne.IncentiveCreator,
 			senderBalance: sdk.NewCoins(
 				sdk.NewCoin(
 					incentiveRecordOne.IncentiveDenom,
@@ -2767,7 +2772,7 @@ func (s *KeeperTestSuite) TestCreateIncentive() {
 		},
 		"record with different incentive amount": {
 			poolId: defaultPoolId,
-			sender: s.TestAccs[0],
+			sender: incentiveRecordOne.IncentiveCreator,
 			senderBalance: sdk.NewCoins(
 				sdk.NewCoin(
 					incentiveRecordOne.IncentiveDenom,
@@ -2778,7 +2783,7 @@ func (s *KeeperTestSuite) TestCreateIncentive() {
 		},
 		"existing incentive records": {
 			poolId: defaultPoolId,
-			sender: s.TestAccs[0],
+			sender: incentiveRecordOne.IncentiveCreator,
 			senderBalance: sdk.NewCoins(
 				sdk.NewCoin(
 					incentiveRecordOne.IncentiveDenom,
@@ -2795,7 +2800,7 @@ func (s *KeeperTestSuite) TestCreateIncentive() {
 			isInvalidPoolId: true,
 
 			poolId: defaultPoolId,
-			sender: s.TestAccs[0],
+			sender: incentiveRecordOne.IncentiveCreator,
 			senderBalance: sdk.NewCoins(
 				sdk.NewCoin(
 					incentiveRecordOne.IncentiveDenom,
@@ -2808,7 +2813,7 @@ func (s *KeeperTestSuite) TestCreateIncentive() {
 		},
 		"zero incentive amount": {
 			poolId: defaultPoolId,
-			sender: s.TestAccs[0],
+			sender: incentiveRecordOne.IncentiveCreator,
 			senderBalance: sdk.NewCoins(
 				sdk.NewCoin(
 					incentiveRecordOne.IncentiveDenom,
@@ -2821,7 +2826,7 @@ func (s *KeeperTestSuite) TestCreateIncentive() {
 		},
 		"negative incentive amount": {
 			poolId: defaultPoolId,
-			sender: s.TestAccs[0],
+			sender: incentiveRecordOne.IncentiveCreator,
 			senderBalance: sdk.NewCoins(
 				sdk.NewCoin(
 					incentiveRecordOne.IncentiveDenom,
@@ -2834,7 +2839,7 @@ func (s *KeeperTestSuite) TestCreateIncentive() {
 		},
 		"start time too early": {
 			poolId: defaultPoolId,
-			sender: s.TestAccs[0],
+			sender: incentiveRecordOne.IncentiveCreator,
 			senderBalance: sdk.NewCoins(
 				sdk.NewCoin(
 					incentiveRecordOne.IncentiveDenom,
@@ -2847,7 +2852,7 @@ func (s *KeeperTestSuite) TestCreateIncentive() {
 		},
 		"zero emission rate": {
 			poolId: defaultPoolId,
-			sender: s.TestAccs[0],
+			sender: incentiveRecordOne.IncentiveCreator,
 			senderBalance: sdk.NewCoins(
 				sdk.NewCoin(
 					incentiveRecordOne.IncentiveDenom,
@@ -2860,7 +2865,7 @@ func (s *KeeperTestSuite) TestCreateIncentive() {
 		},
 		"negative emission rate": {
 			poolId: defaultPoolId,
-			sender: s.TestAccs[0],
+			sender: incentiveRecordOne.IncentiveCreator,
 			senderBalance: sdk.NewCoins(
 				sdk.NewCoin(
 					incentiveRecordOne.IncentiveDenom,
@@ -2873,7 +2878,7 @@ func (s *KeeperTestSuite) TestCreateIncentive() {
 		},
 		"unsupported min uptime": {
 			poolId: defaultPoolId,
-			sender: s.TestAccs[0],
+			sender: incentiveRecordOne.IncentiveCreator,
 			senderBalance: sdk.NewCoins(
 				sdk.NewCoin(
 					incentiveRecordOne.IncentiveDenom,
@@ -2886,7 +2891,7 @@ func (s *KeeperTestSuite) TestCreateIncentive() {
 		},
 		"insufficient sender balance": {
 			poolId:        defaultPoolId,
-			sender:        s.TestAccs[0],
+			sender:        incentiveRecordOne.IncentiveCreator,
 			senderBalance: sdk.NewCoins(),
 			recordToSet:   incentiveRecordOne,
 
@@ -2925,7 +2930,7 @@ func (s *KeeperTestSuite) TestCreateIncentive() {
 				s.Require().ErrorContains(err, tc.expectedError.Error())
 
 				// Ensure nothing was placed in state
-				recordInState, err := clKeeper.GetIncentiveRecord(s.Ctx, tc.poolId, tc.recordToSet.IncentiveDenom, tc.recordToSet.MinUptime)
+				recordInState, err := clKeeper.GetIncentiveRecord(s.Ctx, tc.poolId, tc.recordToSet.IncentiveDenom, tc.recordToSet.MinUptime, tc.sender)
 				s.Require().Error(err)
 				s.Require().Equal(types.IncentiveRecord{}, recordInState)
 
@@ -2935,13 +2940,13 @@ func (s *KeeperTestSuite) TestCreateIncentive() {
 			s.Require().NoError(err)
 
 			// Returned incentive record should equal both to what's in state and what we expect
-			recordInState, err := clKeeper.GetIncentiveRecord(s.Ctx, tc.poolId, tc.recordToSet.IncentiveDenom, tc.recordToSet.MinUptime)
+			recordInState, err := clKeeper.GetIncentiveRecord(s.Ctx, tc.poolId, tc.recordToSet.IncentiveDenom, tc.recordToSet.MinUptime, tc.sender)
 			s.Require().Equal(tc.recordToSet, recordInState)
 			s.Require().Equal(tc.recordToSet, incentiveRecord)
 
 			// Ensure that existing records aren't affected
 			for _, incentiveRecord := range tc.existingRecords {
-				_, err := clKeeper.GetIncentiveRecord(s.Ctx, tc.poolId, incentiveRecord.IncentiveDenom, incentiveRecord.MinUptime)
+				_, err := clKeeper.GetIncentiveRecord(s.Ctx, tc.poolId, incentiveRecord.IncentiveDenom, incentiveRecord.MinUptime, incentiveRecord.IncentiveCreator)
 				s.Require().NoError(err)
 			}
 		})
@@ -3031,25 +3036,25 @@ func (s *KeeperTestSuite) TestClaimAllIncentives() {
 		growthInside      []sdk.DecCoins
 		growthOutside     []sdk.DecCoins
 		forfeitIncentives bool
-		expectedError       error
+		expectedError     error
 	}{
 		"happy path: claim rewards without forfeiting": {
-			poolId: validPoolId,
+			poolId:        validPoolId,
 			growthInside:  uptimeHelper.hundredTokensMultiDenom,
 			growthOutside: uptimeHelper.twoHundredTokensMultiDenom,
 		},
 		"claim and forfeit rewards": {
-			poolId: validPoolId,
+			poolId:            validPoolId,
 			growthInside:      uptimeHelper.hundredTokensMultiDenom,
 			growthOutside:     uptimeHelper.twoHundredTokensMultiDenom,
 			forfeitIncentives: true,
 		},
 		"claim and forfeit rewards when no rewards have accrued": {
-			poolId: validPoolId,
+			poolId:            validPoolId,
 			forfeitIncentives: true,
 		},
 		"claim and forfeit rewards with varying amounts and different denoms": {
-			poolId: validPoolId,
+			poolId:            validPoolId,
 			growthInside:      uptimeHelper.varyingTokensMultiDenom,
 			growthOutside:     uptimeHelper.varyingTokensSingleDenom,
 			forfeitIncentives: true,
@@ -3058,7 +3063,7 @@ func (s *KeeperTestSuite) TestClaimAllIncentives() {
 		// error catching
 
 		"error: non existent pool/accum": {
-			poolId: validPoolId + 1,
+			poolId:        validPoolId + 1,
 			growthInside:  uptimeHelper.hundredTokensMultiDenom,
 			growthOutside: uptimeHelper.twoHundredTokensMultiDenom,
 
```

### x/concentrated-liquidity/store.go
```diff
@@ -156,12 +156,13 @@ func ParseFullIncentiveRecordFromBz(key []byte, value []byte) (incentiveRecord t
 	// These may include irrelevant parts of the prefix such as the module prefix.
 	incentiveRecordKeyComponents := strings.Split(keyStr, types.KeySeparator)
 
-	// We only care about the last 3 components, which are:
+	// We only care about the last 4 components, which are:
 	// - pool id
 	// - incentive denom
 	// - min uptime
+	// - incentive creator
 
-	relevantIncentiveKeyComponents := incentiveRecordKeyComponents[len(incentiveRecordKeyComponents)-3:]
+	relevantIncentiveKeyComponents := incentiveRecordKeyComponents[len(incentiveRecordKeyComponents)-4:]
 
 	incentivePrefix := incentiveRecordKeyComponents[0]
 	if incentivePrefix != string(types.IncentivePrefix) {
@@ -180,17 +181,24 @@ func ParseFullIncentiveRecordFromBz(key []byte, value []byte) (incentiveRecord t
 		return types.IncentiveRecord{}, err
 	}
 
+	// Note that we skip the first byte since we prefix addresses by length in key
+	incentiveCreator := sdk.AccAddress(relevantIncentiveKeyComponents[3][1:])
+	if err != nil {
+		return types.IncentiveRecord{}, err
+	}
+
 	incentiveBody, err := ParseIncentiveRecordBodyFromBz(value)
 	if err != nil {
 		return types.IncentiveRecord{}, err
 	}
 
 	return types.IncentiveRecord{
-		PoolId:          poolId,
-		IncentiveDenom:  incentiveDenom,
-		RemainingAmount: incentiveBody.RemainingAmount,
-		EmissionRate:    incentiveBody.EmissionRate,
-		StartTime:       incentiveBody.StartTime,
-		MinUptime:       time.Duration(minUptime),
+		PoolId:           poolId,
+		IncentiveDenom:   incentiveDenom,
+		IncentiveCreator: incentiveCreator,
+		RemainingAmount:  incentiveBody.RemainingAmount,
+		EmissionRate:     incentiveBody.EmissionRate,
+		StartTime:        incentiveBody.StartTime,
+		MinUptime:        time.Duration(minUptime),
 	}, nil
 }
```

### x/concentrated-liquidity/types/errors.go
```diff
@@ -226,13 +226,14 @@ func (e InvalidSwapFeeError) Error() string {
 }
 
 type IncentiveRecordNotFoundError struct {
-	PoolId         uint64
-	IncentiveDenom string
-	MinUptime      time.Duration
+	PoolId              uint64
+	IncentiveDenom      string
+	MinUptime           time.Duration
+	IncentiveCreatorStr string
 }
 
 func (e IncentiveRecordNotFoundError) Error() string {
-	return fmt.Sprintf("incentive record not found. pool id (%d), incentive denom (%s), minimum uptime (%s)", e.PoolId, e.IncentiveDenom, e.MinUptime.String())
+	return fmt.Sprintf("incentive record not found. pool id (%d), incentive denom (%s), minimum uptime (%s), incentive creator (%s)", e.PoolId, e.IncentiveDenom, e.MinUptime.String(), e.IncentiveCreatorStr)
 }
 
 type StartTimeTooEarlyError struct {
```

### x/concentrated-liquidity/types/incentive_record.go
```diff
@@ -15,6 +15,10 @@ type IncentiveRecord struct {
 	// incentive_denom is the denom of the token being distributed as part of this incentive record
 	IncentiveDenom string
 
+	// incentiveCreator is the address that created the incentive record. This address does not have any special
+	// privileges – it is only kept to keep incentive records created by different addresses separate.
+	IncentiveCreator sdk.AccAddress
+
 	// remaining_amount is the total amount of incentives to be distributed
 	RemainingAmount sdk.Dec
 
```

### x/concentrated-liquidity/types/keys.go
```diff
@@ -5,6 +5,7 @@ import (
 	"time"
 
 	sdk "github.com/cosmos/cosmos-sdk/types"
+	"github.com/cosmos/cosmos-sdk/types/address"
 
 	"github.com/osmosis-labs/osmosis/osmoutils"
 )
@@ -89,8 +90,9 @@ func KeyPool(poolId uint64) []byte {
 	return []byte(fmt.Sprintf("%s%d", PoolPrefix, poolId))
 }
 
-func KeyIncentiveRecord(poolId uint64, denom string, minUptime time.Duration) []byte {
-	return []byte(fmt.Sprintf("%s%s%d%s%s%s%d", IncentivePrefix, KeySeparator, poolId, KeySeparator, denom, KeySeparator, uint64(minUptime)))
+func KeyIncentiveRecord(poolId uint64, denom string, minUptime time.Duration, addr sdk.AccAddress) []byte {
+	addrKey := address.MustLengthPrefix(addr.Bytes())
+	return []byte(fmt.Sprintf("%s%s%d%s%s%s%d%s%s", IncentivePrefix, KeySeparator, poolId, KeySeparator, denom, KeySeparator, uint64(minUptime), KeySeparator, addrKey))
 }
 
 func KeyPoolIncentiveRecords(poolId uint64) []byte {
```
