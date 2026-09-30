# [?] fix(e2e): remove taker fee non-determinism affecting geo twap in e2e (#6271)

## Summary
Severity: Unknown
Chain: Osmosis
Component: osmosis-labs/osmosis
Published: 2023-09-02
Source: https://github.com/osmosis-labs/osmosis/commit/2e72ee656e4812280528f95ba25ab5143828ecf6
Type: security-commit

## Details
fix(e2e): remove taker fee non-determinism affecting geo twap in e2e (#6271)

* try removing taker fee non-determinism affecting geo twap in e2e

* updates

* updates

* similar fix for CreateConcentratedLiquidityPoolVoting_And_TWAP

## Patch
### tests/e2e/e2e_test.go
```diff
@@ -45,9 +45,9 @@ var (
 // TODO: Find more scalable way to do this
 func (s *IntegrationTestSuite) TestAllE2E() {
 	// Reset the default taker fee to 0.15%, so we can actually run tests with it activated
-	s.T().Run("SetDefaultTakerFeeBothChains", func(t *testing.T) {
-		s.T().Log("resetting the default taker fee to 0.15%")
-		s.SetDefaultTakerFeeBothChains()
+	s.T().Run("SetDefaultTakerFeeChainB", func(t *testing.T) {
+		s.T().Log("resetting the default taker fee to 0.15% on chain B only")
+		s.SetDefaultTakerFeeChainB()
 	})
 
 	// Zero Dependent Tests
@@ -301,6 +301,8 @@ func (s *IntegrationTestSuite) ProtoRev() {
 	s.Require().Equal(profits, routeStats[0].Profits)
 }
 
+// Note: this test depends on taker fee being set.
+// As a result, we use chain B. Chain A has zero taker fee.
 func (s *IntegrationTestSuite) ConcentratedLiquidity() {
 	var (
 		denom0                 = "uion"
@@ -311,37 +313,38 @@ func (s *IntegrationTestSuite) ConcentratedLiquidity() {
 		takerFee               = osmomath.MustNewDecFromStr("0.0015")
 	)
 
-	chainAB, chainABNode, err := s.getChainCfgs()
+	// Use chain B node since it has taker fee enabled.
+	chainB, chainBNode, err := s.getChainBCfgs()
 	s.Require().NoError(err)
 
 	// Get the permisionless pool creation parameter.
-	isPermisionlessCreationEnabledStr := chainABNode.QueryParams(cltypes.ModuleName, string(cltypes.KeyIsPermisionlessPoolCreationEnabled))
+	isPermisionlessCreationEnabledStr := chainBNode.QueryParams(cltypes.ModuleName, string(cltypes.KeyIsPermisionlessPoolCreationEnabled))
 	if !strings.EqualFold(isPermisionlessCreationEnabledStr, "false") {
 		s.T().Fatal("concentrated liquidity pool creation is enabled when should not have been")
 	}
 
 	// Change the parameter to enable permisionless pool creation.
-	err = chainABNode.ParamChangeProposal("concentratedliquidity", string(cltypes.KeyIsPermisionlessPoolCreationEnabled), []byte("true"), chainAB)
+	err = chainBNode.ParamChangeProposal("concentratedliquidity", string(cltypes.KeyIsPermisionlessPoolCreationEnabled), []byte("true"), chainB)
 	s.Require().NoError(err)
 
 	// Update the protorev admin address to a known wallet we can control
-	adminWalletAddr := chainABNode.CreateWalletAndFund("admin", []string{"4000000uosmo"}, chainAB)
-	err = chainABNode.ParamChangeProposal("protorev", string(protorevtypes.ParamStoreKeyAdminAccount), []byte(fmt.Sprintf(`"%s"`, adminWalletAddr)), chainAB)
+	adminWalletAddr := chainBNode.CreateWalletAndFund("admin", []string{"4000000uosmo"}, chainB)
+	err = chainBNode.ParamChangeProposal("protorev", string(protorevtypes.ParamStoreKeyAdminAccount), []byte(fmt.Sprintf(`"%s"`, adminWalletAddr)), chainB)
 	s.Require().NoError(err)
 
 	// Update the weight of CL pools so that this test case is not back run by protorev.
-	chainABNode.SetMaxPoolPointsPerTx(7, adminWalletAddr)
+	chainBNode.SetMaxPoolPointsPerTx(7, adminWalletAddr)
 
 	// Confirm that the parameter has been changed.
-	isPermisionlessCreationEnabledStr = chainABNode.QueryParams(cltypes.ModuleName, string(cltypes.KeyIsPermisionlessPoolCreationEnabled))
+	isPermisionlessCreationEnabledStr = chainBNode.QueryParams(cltypes.ModuleName, string(cltypes.KeyIsPermisionlessPoolCreationEnabled))
 	if !strings.EqualFold(isPermisionlessCreationEnabledStr, "true") {
 		s.T().Fatal("concentrated liquidity pool creation is not enabled")
 	}
 
 	// Create concentrated liquidity pool when permisionless pool creation is enabled.
-	poolID := chainABNode.CreateConcentratedPool(initialization.ValidatorWalletName, denom0, denom1, tickSpacing, spreadFactor)
+	poolID := chainBNode.CreateConcentratedPool(initialization.ValidatorWalletName, denom0, denom1, tickSpacing, spreadFactor)
 
-	concentratedPool := s.updatedConcentratedPool(chainABNode, poolID)
+	concentratedPool := s.updatedConcentratedPool(chainBNode, poolID)
 
 	// Sanity check that pool initialized with valid parameters (the ones that we haven't explicitly specified)
 	s.Require().Equal(concentratedPool.GetCurrentTick(), int64(0))
@@ -359,36 +362,36 @@ func (s *IntegrationTestSuite) ConcentratedLiquidity() {
 	fundTokens := []string{"100000000uosmo", "100000000uion", "100000000stake"}
 
 	// Get 3 addresses to create positions
-	address1 := chainABNode.CreateWalletAndFund("addr1", fundTokens, chainAB)
-	address2 := chainABNode.CreateWalletAndFund("addr2", fundTokens, chainAB)
-	address3 := chainABNode.CreateWalletAndFund("addr3", fundTokens, chainAB)
+	address1 := chainBNode.CreateWalletAndFund("addr1", fundTokens, chainB)
+	address2 := chainBNode.CreateWalletAndFund("addr2", fundTokens, chainB)
+	address3 := chainBNode.CreateWalletAndFund("addr3", fundTokens, chainB)
 
 	// When claiming rewards, a small portion of dust is forfeited and is redistributed to everyone. We must track the total
 	// liquidity across all positions (even if not active), in order to calculate how much to increase the reward growth global per share by.
 	totalLiquidity := osmomath.ZeroDec()
 
 	// Create 2 positions for address1: overlap together, overlap with 2 address3 positions
-	_, liquidity := chainABNode.CreateConcentratedPosition(address1, "[-120000]", "40000", fmt.Sprintf("10000000%s,10000000%s", denom0, denom1), 0, 0, poolID)
+	_, liquidity := chainBNode.CreateConcentratedPosition(address1, "[-120000]", "40000", fmt.Sprintf("10000000%s,10000000%s", denom0, denom1), 0, 0, poolID)
 	totalLiquidity = totalLiquidity.Add(liquidity)
-	_, liquidity = chainABNode.CreateConcentratedPosition(address1, "[-40000]", "120000", fmt.Sprintf("10000000%s,10000000%s", denom0, denom1), 0, 0, poolID)
+	_, liquidity = chainBNode.CreateConcentratedPosition(address1, "[-40000]", "120000", fmt.Sprintf("10000000%s,10000000%s", denom0, denom1), 0, 0, poolID)
 	totalLiquidity = totalLiquidity.Add(liquidity)
 
 	// Create 1 position for address2: does not overlap with anything, ends at maximum
-	_, liquidity = chainABNode.CreateConcentratedPosition(address2, "220000", fmt.Sprintf("%d", cltypes.MaxTick), fmt.Sprintf("10000000%s,10000000%s", denom0, denom1), 0, 0, poolID)
+	_, liquidity = chainBNode.CreateConcentratedPosition(address2, "220000", fmt.Sprintf("%d", cltypes.MaxTick), fmt.Sprintf("10000000%s,10000000%s", denom0, denom1), 0, 0, poolID)
 	totalLiquidity = totalLiquidity.Add(liquidity)
 
 	// Create 2 positions for address3: overlap together, overlap with 2 address1 positions, one position starts from minimum
-	_, liquidity = chainABNode.CreateConcentratedPosition(address3, "[-160000]", "[-20000]", fmt.Sprintf("10000000%s,10000000%s", denom0, denom1), 0, 0, poolID)
+	_, liquidity = chainBNode.CreateConcentratedPosition(address3, "[-160000]", "[-20000]", fmt.Sprintf("10000000%s,10000000%s", denom0, denom1), 0, 0, poolID)
 	totalLiquidity = totalLiquidity.Add(liquidity)
-	_, liquidity = chainABNode.CreateConcentratedPosition(address3, fmt.Sprintf("[%d]", cltypes.MinInitializedTick), "140000", fmt.Sprintf("10000000%s,10000000%s", denom0, denom1), 0, 0, poolID)
+	_, liquidity = chainBNode.CreateConcentratedPosition(address3, fmt.Sprintf("[%d]", cltypes.MinInitializedTick), "140000", fmt.Sprintf("10000000%s,10000000%s", denom0, denom1), 0, 0, poolID)
 	totalLiquidity = totalLiquidity.Add(liquidity)
 
 	// Get newly created positions
-	positionsAddress1 := chainABNode.QueryConcentratedPositions(address1)
-	positionsAddress2 := chainABNode.QueryConcentratedPositions(address2)
-	positionsAddress3 := chainABNode.QueryConcentratedPositions(address3)
+	positionsAddress1 := chainBNode.QueryConcentratedPositions(address1)
+	positionsAddress2 := chainBNode.QueryConcentratedPositions(address2)
+	positionsAddress3 := chainBNode.QueryConcentratedPositions(address3)
 
-	concentratedPool = s.updatedConcentratedPool(chainABNode, poolID)
+	concentratedPool = s.updatedConcentratedPool(chainBNode, poolID)
 
 	// Assert number of positions per address
 	s.Require().Equal(len(positionsAddress1), 2)
@@ -434,7 +437,7 @@ func (s *IntegrationTestSuite) ConcentratedLiquidity() {
 		uosmoIn_Swap1    = fmt.Sprintf("%suosmo", uosmoInDec_Swap1.Dec().String())
 	)
 	// Perform swap (not crossing initialized ticks)
-	chainABNode.SwapExactAmountIn(uosmoIn_Swap1, outMinAmt, fmt.Sprintf("%d", poolID), denom0, initialization.ValidatorWalletName)
+	chainBNode.SwapExactAmountIn(uosmoIn_Swap1, outMinAmt, fmt.Sprintf("%d", poolID), denom0, initialization.ValidatorWalletName)
 	// Calculate and track global spread reward growth for swap 1
 	uosmoInDec_Swap1_SubTakerFee := uosmoInDec_Swap1.Dec().Mul(osmomath.OneDec().Sub(takerFee)).TruncateDec()
 	uosmoInDec_Swap1_SubTakerFee_SubSpreadFactor := uosmoInDec_Swap1_SubTakerFee.Mul(osmomath.OneDec().Sub(spreadFactorDec))
@@ -446,7 +449,7 @@ func (s *IntegrationTestSuite) ConcentratedLiquidity() {
 	liquidityBeforeSwap := concentratedPool.GetLiquidity()
 	sqrtPriceBeforeSwap := concentratedPool.GetCurrentSqrtPrice()
 
-	concentratedPool = s.updatedConcentratedPool(chainABNode, poolID)
+	concentratedPool = s.updatedConcentratedPool(chainBNode, poolID)
 
 	liquidityAfterSwap := concentratedPool.GetLiquidity()
 	sqrtPriceAfterSwap := concentratedPool.GetCurrentSqrtPrice()
@@ -462,9 +465,9 @@ func (s *IntegrationTestSuite) ConcentratedLiquidity() {
 	// Collect SpreadRewards: Swap 1
 
 	// Track balances for address1 position1
-	addr1BalancesBefore := s.addrBalance(chainABNode, address1)
-	chainABNode.CollectSpreadRewards(address1, fmt.Sprint(positionsAddress1[0].Position.PositionId))
-	addr1BalancesAfter := s.addrBalance(chainABNode, address1)
+	addr1BalancesBefore := s.addrBalance(chainBNode, address1)
+	chainBNode.CollectSpreadRewards(address1, fmt.Sprint(positionsAddress1[0].Position.PositionId))
+	addr1BalancesAfter := s.addrBalance(chainBNode, address1)
 
 	// Assert that the balance changed only for tokenIn (uosmo)
 	s.assertBalancesInvariants(addr1BalancesBefore, addr1BalancesAfter, false, true)
@@ -550,13 +553,13 @@ func (s *IntegrationTestSuite) ConcentratedLiquidity() {
 	uosmoIn_Swap2 := fmt.Sprintf("%suosmo", uosmoInDec_Swap2_AddTakerFee.String())
 
 	// Perform a swap
-	chainABNode.SwapExactAmountIn(uosmoIn_Swap2, outMinAmt, fmt.Sprintf("%d", poolID), denom0, initialization.ValidatorWalletName)
+	chainBNode.SwapExactAmountIn(uosmoIn_Swap2, outMinAmt, fmt.Sprintf("%d", poolID), denom0, initialization.ValidatorWalletName)
 
 	// Calculate the amount of liquidity of the position that was kicked out during swap (address1 position1)
 	liquidityOfKickedOutPosition := positionsAddress1[0].Position.Liquidity
 
 	// Update pool and track pool's liquidity
-	concentratedPool = s.updatedConcentratedPool(chainABNode, poolID)
+	concentratedPool = s.updatedConcentratedPool(chainBNode, poolID)
 
 	liquidityAfterSwap = concentratedPool.GetLiquidity()
 
@@ -589,9 +592,9 @@ func (s *IntegrationTestSuite) ConcentratedLiquidity() {
 	// Assert that address1 position1 earned spread rewards only from first swap step
 
 	// Track balances for address1 position1
-	addr1BalancesBefore = s.addrBalance(chainABNode, address1)
-	chainABNode.CollectSpreadRewards(address1, fmt.Sprint(positionsAddress1[0].Position.PositionId))
-	addr1BalancesAfter = s.addrBalance(chainABNode, address1)
+	addr1BalancesBefore = s.addrBalance(chainBNode, address1)
+	chainBNode.CollectSpreadRewards(address1, fmt.Sprint(positionsAddress1[0].Position.PositionId))
+	addr1BalancesAfter = s.addrBalance(chainBNode, address1)
 
 	// Assert that the balance changed only for tokenIn (uosmo)
 	s.assertBalancesInvariants(addr1BalancesBefore, addr1BalancesAfter, false, true)
@@ -614,9 +617,9 @@ func (s *IntegrationTestSuite) ConcentratedLiquidity() {
 	// Assert that address3 position2 earned rewards from first and second swaps
 
 	// Track balance off address3 position2: check that position that has not been kicked out earned full rewards
-	addr3BalancesBefore := s.addrBalance(chainABNode, address3)
-	chainABNode.CollectSpreadRewards(address3, fmt.Sprint(positionsAddress3[1].Position.PositionId))
-	addr3BalancesAfter := s.addrBalance(chainABNode, address3)
+	addr3BalancesBefore := s.addrBalance(chainBNode, address3)
+	chainBNode.CollectSpreadRewards(address3, fmt.Sprint(positionsAddress3[1].Position.PositionId))
+	addr3BalancesAfter := s.addrBalance(chainBNode, address3)
 
 	// Calculate uncollected spread rewards for address3 position2 earned from Swap 1
 	spreadRewardsUncollectedAddress3Position2_Swap1 := calculateUncollectedSpreadRewards(
@@ -685,7 +688,7 @@ func (s *IntegrationTestSuite) ConcentratedLiquidity() {
 	amountInToGetToNextInitTick = liquidityBeforeSwap.Mul(fractionAtNextInitializedTick.Dec())
 
 	// Collect spread rewards for address1 position1 to avoid overhead computations (swap2 already asserted spread rewards are aggregated correctly from multiple swaps)
-	chainABNode.CollectSpreadRewards(address1, fmt.Sprint(positionsAddress1[0].Position.PositionId))
+	chainBNode.CollectSpreadRewards(address1, fmt.Sprint(positionsAddress1[0].Position.PositionId))
 
 	var (
 		// Swap parameters
@@ -701,18 +704,18 @@ func (s *IntegrationTestSuite) ConcentratedLiquidity() {
 	uionIn_Swap3 := fmt.Sprintf("%suion", uionInDec_Swap3_AddTakerFee.String())
 
 	// Perform a swap
-	chainABNode.SwapExactAmountIn(uionIn_Swap3, outMinAmt, fmt.Sprintf("%d", poolID), denom1, initialization.ValidatorWalletName)
+	chainBNode.SwapExactAmountIn(uionIn_Swap3, outMinAmt, fmt.Sprintf("%d", poolID), denom1, initialization.ValidatorWalletName)
 
 	// Assert liquidity of kicked in position was successfully added to the pool
-	concentratedPool = s.updatedConcentratedPool(chainABNode, poolID)
+	concentratedPool = s.updatedConcentratedPool(chainBNode, poolID)
 
 	liquidityAfterSwap = concentratedPool.GetLiquidity()
 	s.Require().Equal(liquidityBeforeSwap.Add(positionsAddress1[0].Position.Liquidity), liquidityAfterSwap)
 
 	// Track balance of address1
-	addr1BalancesBefore = s.addrBalance(chainABNode, address1)
-	chainABNode.CollectSpreadRewards(address1, fmt.Sprint(positionsAddress1[0].Position.PositionId))
-	addr1BalancesAfter = s.addrBalance(chainABNode, address1)
+	addr1BalancesBefore = s.addrBalance(chainBNode, address1)
+	chainBNode.CollectSpreadRewards(address1, fmt.Sprint(positionsAddress1[0].Position.PositionId))
+	addr1BalancesAfter = s.addrBalance(chainBNode, address1)
 
 	// Assert that the balance changed only for tokenIn (uion)
 	s.assertBalancesInvariants(addr1BalancesBefore, addr1BalancesAfter, true, false)
@@ -756,9 +759,9 @@ func (s *IntegrationTestSuite) ConcentratedLiquidity() {
 	// Assert position that was active throughout the whole swap:
 
 	// Track balance of address3
-	addr3BalancesBefore = s.addrBalance(chainABNode, address3)
-	chainABNode.CollectSpreadRewards(address3, fmt.Sprint(positionsAddress3[1].Position.PositionId))
-	addr3BalancesAfter = s.addrBalance(chainABNode, address3)
+	addr3BalancesBefore = s.addrBalance(chainBNode, address3)
+	chainBNode.CollectSpreadRewards(address3, fmt.Sprint(positionsAddress3[1].Position.PositionId))
+	addr3BalancesAfter = s.addrBalance(chainBNode, address3)
 
 	// Assert that the balance changed only for tokenIn (uion)
 	s.assertBalancesInvariants(addr3BalancesBefore, addr3BalancesAfter, true, false)
@@ -797,17 +800,17 @@ func (s *IntegrationTestSuite) ConcentratedLiquidity() {
 	// Assert that positions, which were not included in swaps, were not affected
 
 	// Address3 Position1: [-160000; -20000]
-	addr3BalancesBefore = s.addrBalance(chainABNode, address3)
-	chainABNode.CollectSpreadRewards(address3, fmt.Sprint(positionsAddress3[0].Position.PositionId))
-	addr3BalancesAfter = s.addrBalance(chainABNode, address3)
+	addr3BalancesBefore = s.addrBalance(chainBNode, address3)
+	chainBNode.CollectSpreadRewards(address3, fmt.Sprint(positionsAddress3[0].Position.PositionId))
+	addr3BalancesAfter = s.addrBalance(chainBNode, address3)
 
 	// Assert that balances did not change for any token
 	s.assertBalancesInvariants(addr3BalancesBefore, addr3BalancesAfter, true, true)
 
 	// Address2's only position: [220000; 342000]
-	addr2BalancesBefore := s.addrBalance(chainABNode, address2)
-	chainABNode.CollectSpreadRewards(address2, fmt.Sprint(positionsAddress2[0].Position.PositionId))
-	addr2BalancesAfter := s.addrBalance(chainABNode, address2)
+	addr2BalancesBefore := s.addrBalance(chainBNode, address2)
+	chainBNode.CollectSpreadRewards(address2, fmt.Sprint(positionsAddress2[0].Position.PositionId))
+	addr2BalancesAfter := s.addrBalance(chainBNode, address2)
 
 	// Assert the balances did not change for every token
 	s.assertBalancesInvariants(addr2BalancesBefore, addr2BalancesAfter, true, true)
@@ -817,41 +820,41 @@ func (s *IntegrationTestSuite) ConcentratedLiquidity() {
 	// Withdraw Position parameters
 	defaultLiquidityRemoval := "1000"
 
-	chainAB.WaitForNumHeights(2)
+	chainB.WaitForNumHeights(2)
 
 	// Assert removing some liquidity
 	// address1: check removing some amount of liquidity
 	address1position1liquidityBefore := positionsAddress1[0].Position.Liquidity
-	chainABNode.WithdrawPosition(address1, defaultLiquidityRemoval, positionsAddress1[0].Position.PositionId)
+	chainBNode.WithdrawPosition(address1, defaultLiquidityRemoval, positionsAddress1[0].Position.PositionId)
 	// assert
-	positionsAddress1 = chainABNode.QueryConcentratedPositions(address1)
+	positionsAddress1 = chainBNode.QueryConcentratedPositions(address1)
 	s.Require().Equal(address1position1liquidityBefore, positionsAddress1[0].Position.Liquidity.Add(osmomath.MustNewDecFromStr(defaultLiquidityRemoval)))
 
 	// address2: check removing some amount of liquidity
 	address2position1liquidityBefore := positionsAddress2[0].Position.Liquidity
-	chainABNode.WithdrawPosition(address2, defaultLiquidityRemoval, positionsAddress2[0].Position.PositionId)
+	chainBNode.WithdrawPosition(address2, defaultLiquidityRemoval, positionsAddress2[0].Position.PositionId)
 	// assert
-	positionsAddress2 = chainABNode.QueryConcentratedPositions(address2)
+	positionsAddress2 = chainBNode.QueryConcentratedPositions(address2)
 	s.Require().Equal(address2position1liquidityBefore, positionsAddress2[0].Position.Liquidity.Add(osmomath.MustNewDecFromStr(defaultLiquidityRemoval)))
 
 	// address3: check removing some amount of liquidity
 	address3position1liquidityBefore := positionsAddress3[0].Position.Liquidity
-	chainABNode.WithdrawPosition(address3, defaultLiquidityRemoval, positionsAddress3[0].Position.PositionId)
+	chainBNode.WithdrawPosition(address3, defaultLiquidityRemoval, positionsAddress3[0].Position.PositionId)
 	// assert
-	positionsAddress3 = chainABNode.QueryConcentratedPositions(address3)
+	positionsAddress3 = chainBNode.QueryConcentratedPositions(address3)
 	s.Require().Equal(address3position1liquidityBefore, positionsAddress3[0].Position.Liquidity.Add(osmomath.MustNewDecFromStr(defaultLiquidityRemoval)))
 
 	// Assert removing all liquidity
 	// address2: no more positions left
 	allLiquidityAddress2Position1 := positionsAddress2[0].Position.Liquidity
-	chainABNode.WithdrawPosition(address2, allLiquidityAddress2Position1.String(), positionsAddress2[0].Position.PositionId)
-	positionsAddress2 = chainABNode.QueryConcentratedPositions(address2)
+	chainBNode.WithdrawPosition(address2, allLiquidityAddress2Position1.String(), positionsAddress2[0].Position.PositionId)
+	positionsAddress2 = chainBNode.QueryConcentratedPositions(address2)
 	s.Require().Empty(positionsAddress2)
 
 	// address1: one position left
 	allLiquidityAddress1Position1 := positionsAddress1[0].Position.Liquidity
-	chainABNode.WithdrawPosition(address1, allLiquidityAddress1Position1.String(), positionsAddress1[0].Position.PositionId)
-	positionsAddress1 = chainABNode.QueryConcentratedPositions(address1)
+	chainBNode.WithdrawPosition(address1, allLiquidityAddress1Position1.String(), positionsAddress1[0].Position.PositionId)
+	positionsAddress1 = chainBNode.QueryConcentratedPositions(address1)
 	s.Require().Equal(len(positionsAddress1), 1)
 
 	// Test tick spacing reduction proposal
@@ -872,15 +875,15 @@ func (s *IntegrationTestSuite) ConcentratedLiquidity() {
 	newTickSpacing := cltypes.AuthorizedTickSpacing[indexOfCurrentTickSpacing-1]
 
 	// Run the tick spacing reduction proposal
-	propNumber := chainABNode.SubmitTickSpacingReductionProposal(fmt.Sprintf("%d,%d", poolID, newTickSpacing), sdk.NewCoin(appparams.BaseCoinUnit, osmomath.NewInt(config.InitialMinExpeditedDeposit)), true)
+	propNumber := chainBNode.SubmitTickSpacingReductionProposal(fmt.Sprintf("%d,%d", poolID, newTickSpacing), sdk.NewCoin(appparams.BaseCoinUnit, osmomath.NewInt(config.InitialMinExpeditedDeposit)), true)
 
-	chainABNode.DepositProposal(propNumber, true)
+	chainBNode.DepositProposal(propNumber, true)
 	totalTimeChan := make(chan time.Duration, 1)
-	go chainABNode.QueryPropStatusTimed(propNumber, "PROPOSAL_STATUS_PASSED", totalTimeChan)
+	go chainBNode.QueryPropStatusTimed(propNumber, "PROPOSAL_STATUS_PASSED", totalTimeChan)
 	var wg sync.WaitGroup
 
 	// TODO: create a helper function for all these go routine yes vote calls.
-	for _, n := range chainAB.NodeConfigs {
+	for _, n := range chainB.NodeConfigs {
 		wg.Add(1)
 		go func(nodeConfig *chain.NodeConfig) {
 			defer wg.Done()
@@ -901,11 +904,11 @@ func (s *IntegrationTestSuite) ConcentratedLiquidity() {
 	}
 
 	// Check that the tick spacing was reduced to the expected new tick spacing
-	concentratedPool = s.updatedConcentratedPool(chainABNode, poolID)
+	concentratedPool = s.updatedConcentratedPool(chainBNode, poolID)
 	s.Require().Equal(newTickSpacing, concentratedPool.GetTickSpacing())
 
 	// Reset the maximum number of pool points
-	chainABNode.SetMaxPoolPointsPerTx(int(protorevtypes.DefaultMaxPoolPointsPerTx), adminWalletAddr)
+	chainBNode.SetMaxPoolPointsPerTx(int(protorevtypes.DefaultMaxPoolPointsPerTx), adminWalletAddr)
 }
 
 func (s *IntegrationTestSuite) StableSwapPostUpgrade() {
@@ -1075,11 +1078,14 @@ func (s *IntegrationTestSuite) SuperfluidVoting() {
 	)
 }
 
+// Note: do not use chain B in this test as it has taker fee set.
+// This TWAP test depends on specific values that might be affected
+// by the taker fee.
 func (s *IntegrationTestSuite) CreateConcentratedLiquidityPoolVoting_And_TWAP() {
-	chainAB, chainABNode, err := s.getChainCfgs()
+	chainA, chainANode, err := s.getChainACfgs()
 	s.Require().NoError(err)
 
-	poolId, err := chainAB.SubmitCreateConcentratedPoolProposal(chainABNode)
+	poolId, err := chainA.SubmitCreateConcentratedPoolProposal(chainANode)
 	s.NoError(err)
 	fmt.Println("poolId", poolId)
 
@@ -1093,7 +1099,7 @@ func (s *IntegrationTestSuite) CreateConcentratedLiquidityPoolVoting_And_TWAP()
 	var concentratedPool cltypes.ConcentratedPoolExtension
 	s.Eventually(
 		func() bool {
-			concentratedPool = s.updatedConcentratedPool(chainABNode, poolId)
+			concentratedPool = s.updatedConcentratedPool(chainANode, poolId)
 			s.Require().Equal(poolmanagertypes.Concentrated, concentratedPool.GetType())
 			s.Require().Equal(expectedDenom0, concentratedPool.GetToken0())
 			s.Require().Equal(expectedDenom1, concentratedPool.GetToken1())
@@ -1110,45 +1116,45 @@ func (s *IntegrationTestSuite) CreateConcentratedLiquidityPoolVoting_And_TWAP()
 	fundTokens := []string{"100000000stake", "100000000uosmo"}
 
 	// Get address to create positions
-	address1 := chainABNode.CreateWalletAndFund("address1", fundTokens, chainAB)
+	address1 := chainANode.CreateWalletAndFund("address1", fundTokens, chainA)
 
 	// We add 5 ms to avoid landing directly on block time in twap. If block time
 	// is provided as start time, the latest spot price is used. Otherwise
 	// interpolation is done.
-	timeBeforePositionCreationBeforeSwap := chainABNode.QueryLatestBlockTime().Add(5 * time.Millisecond)
+	timeBeforePositionCreationBeforeSwap := chainANode.QueryLatestBlockTime().Add(5 * time.Millisecond)
 	s.T().Log("geometric twap, start time ", timeBeforePositionCreationBeforeSwap.Unix())
 
 	// Wait for the next height so that the requested twap
 	// start time (timeBeforePositionCreationBeforeSwap) is not equal to the block time.
-	chainAB.WaitForNumHeights(1)
+	chainA.WaitForNumHeights(1)
 
 	// Check initial TWAP
 	// We expect this to error since there is no spot price yet.
 	s.T().Log("initial twap check")
-	initialTwapBOverA, err := chainABNode.QueryGeometricTwapToNow(concentratedPool.GetId(), concentratedPool.GetToken1(), concentratedPool.GetToken0(), timeBeforePositionCreationBeforeSwap)
+	initialTwapBOverA, err := chainANode.QueryGeometricTwapToNow(concentratedPool.GetId(), concentratedPool.GetToken1(), concentratedPool.GetToken0(), timeBeforePositionCreationBeforeSwap)
 	s.Require().Error(err)
 	s.Require().Equal(osmomath.Dec{}, initialTwapBOverA)
 
 	// Create a position and check that TWAP now returns a value.
 	s.T().Log("creating first position")
-	chainABNode.CreateConcentratedPosition(address1, "[-120000]", "40000", fmt.Sprintf("10000000%s,20000000%s", concentratedPool.GetToken0(), concentratedPool.GetToken1()), 0, 0, concentratedPool.GetId())
-	timeAfterPositionCreationBeforeSwap := chainABNode.QueryLatestBlockTime()
-	chainAB.WaitForNumHeights(2)
-	firstPositionTwapBOverA, err := chainABNode.QueryGeometricTwapToNow(concentratedPool.GetId(), concentratedPool.GetToken1(), concentratedPool.GetToken0(), timeAfterPositionCreationBeforeSwap)
+	chainANode.CreateConcentratedPosition(address1, "[-120000]", "40000", fmt.Sprintf("10000000%s,20000000%s", concentratedPool.GetToken0(), concentratedPool.GetToken1()), 0, 0, concentratedPool.GetId())
+	timeAfterPositionCreationBeforeSwap := chainANode.QueryLatestBlockTime()
+	chainA.WaitForNumHeights(2)
+	firstPositionTwapBOverA, err := chainANode.QueryGeometricTwapToNow(concentratedPool.GetId(), concentratedPool.GetToken1(), concentratedPool.GetToken0(), timeAfterPositionCreationBeforeSwap)
 	s.Require().NoError(err)
 	s.Require().Equal(osmomath.MustNewDecFromStr("0.5"), firstPositionTwapBOverA)
 
 	// Run a swap and check that the TWAP updates.
 	s.T().Log("run swap")
 	coinAIn := fmt.Sprintf("1000000%s", concentratedPool.GetToken0())
-	chainABNode.SwapExactAmountIn(coinAIn, "1", fmt.Sprintf("%d", concentratedPool.GetId()), concentratedPool.GetToken1(), address1)
+	chainANode.SwapExactAmountIn(coinAIn, "1", fmt.Sprintf("%d", concentratedPool.GetId()), concentratedPool.GetToken1(), address1)
 
-	timeAfterSwap := chainABNode.QueryLatestBlockTime()
-	chainAB.WaitForNumHeights(1)
-	timeAfterSwapPlus1Height := chainABNode.QueryLatestBlockTime()
+	timeAfterSwap := chainANode.QueryLatestBlockTime()
+	chainA.WaitForNumHeights(1)
+	timeAfterSwapPlus1Height := chainANode.QueryLatestBlockTime()
 
 	s.T().Log("querying for the TWAP after swap")
-	afterSwapTwapBOverA, err := chainABNode.QueryGeometricTwap(concentratedPool.GetId(), concentratedPool.GetToken1(), concentratedPool.GetToken0(), timeAfterSwap, timeAfterSwapPlus1Height)
+	afterSwapTwapBOverA, err := chainANode.QueryGeometricTwap(concentratedPool.GetId(), concentratedPool.GetToken1(), concentratedPool.GetToken0(), timeAfterSwap, timeAfterSwapPlus1Height)
 	s.Require().NoError(err)
 
 	// We swap stake so uosmo's supply will decrease and stake will increase.
@@ -1157,22 +1163,22 @@ func (s *IntegrationTestSuite) CreateConcentratedLiquidityPoolVoting_And_TWAP()
 
 	// Remove the position and check that TWAP returns an error.
 	s.T().Log("removing first position (pool is drained)")
-	positions := chainABNode.QueryConcentratedPositions(address1)
-	chainABNode.WithdrawPosition(address1, positions[0].Position.Liquidity.String(), positions[0].Position.PositionId)
-	chainAB.WaitForNumHeights(1)
+	positions := chainANode.QueryConcentratedPositions(address1)
+	chainANode.WithdrawPosition(address1, positions[0].Position.Liquidity.String(), positions[0].Position.PositionId)
+	chainA.WaitForNumHeights(1)
 
 	s.T().Log("querying for the TWAP from after pool drained")
-	afterRemoveTwapBOverA, err := chainABNode.QueryGeometricTwapToNow(concentratedPool.GetId(), concentratedPool.GetToken1(), concentratedPool.GetToken0(), timeAfterSwapPlus1Height)
+	afterRemoveTwapBOverA, err := chainANode.QueryGeometricTwapToNow(concentratedPool.GetId(), concentratedPool.GetToken1(), concentratedPool.GetToken0(), timeAfterSwapPlus1Height)
 	s.Require().Error(err)
 	s.Require().Equal(osmomath.Dec{}, afterRemoveTwapBOverA)
 
 	// Create a position and check that TWAP now returns a value.
 	// Should be equal to 1 since the position contains equal amounts of both tokens.
 	s.T().Log("creating position")
-	chainABNode.CreateConcentratedPosition(address1, "[-120000]", "40000", fmt.Sprintf("10000000%s,10000000%s", concentratedPool.GetToken0(), concentratedPool.GetToken1()), 0, 0, concentratedPool.GetId())
-	chainAB.WaitForNumHeights(1)
-	timeAfterSwapRemoveAndCreatePlus1Height := chainABNode.QueryLatestBlockTime()
-	secondTwapBOverA, err := chainABNode.QueryGeometricTwapToNow(concentratedPool.GetId(), concentratedPool.GetToken1(), concentratedPool.GetToken0(), timeAfterSwapRemoveAndCreatePlus1Height)
+	chainANode.CreateConcentratedPosition(address1, "[-120000]", "40000", fmt.Sprintf("10000000%s,10000000%s", concentratedPool.GetToken0(), concentratedPool.GetToken1()), 0, 0, concentratedPool.GetId())
+	chainA.WaitForNumHeights(1)
+	timeAfterSwapRemoveAndCreatePlus1Height := chainANode.QueryLatestBlockTime()
+	secondTwapBOverA, err := chainANode.QueryGeometricTwapToNow(concentratedPool.GetId(), concentratedPool.GetToken1(), concentratedPool.GetToken0(), timeAfterSwapRemoveAndCreatePlus1Height)
 	s.Require().NoError(err)
 	s.Require().Equal(osmomath.NewDec(1), secondTwapBOverA)
 }
@@ -1737,6 +1743,9 @@ func (s *IntegrationTestSuite) ExpeditedProposals() {
 // Assuming base asset is uosmo, the initial twap is 2
 // Upon swapping 1_000_000 uosmo for stake, supply changes, making uosmo less expensive.
 // As a result of the swap, twap changes to 0.5.
+// Note: do not use chain B in this test as it has taker fee set.
+// This TWAP test depends on specific values that might be affected
+// by the taker fee.
 func (s *IntegrationTestSuite) GeometricTWAP() {
 	const (
 		// This pool contains 1_000_000 uosmo and 2_000_000 stake.
@@ -1750,64 +1759,66 @@ func (s *IntegrationTestSuite) GeometricTWAP() {
 		minAmountOut = "1"
 	)
 
-	chainAB, chainABNode, err := s.getChainCfgs()
+	// Note: use chain A specifically as this is the chain where we do not
+	// set taker fee.
+	chainA, chainANode, err := s.getChainACfgs()
 	s.Require().NoError(err)
 
-	sender := chainABNode.GetWallet(initialization.ValidatorWalletName)
+	sender := chainANode.GetWallet(initialization.ValidatorWalletName)
 
 	// Triggers the creation of TWAP records.
-	poolId := chainABNode.CreateBalancerPool(poolFile, initialization.ValidatorWalletName)
-	swapWalletAddr := chainABNode.CreateWalletAndFund(walletName, []string{initialization.WalletFeeTokens.String()}, chainAB)
+	poolId := chainANode.CreateBalancerPool(poolFile, initialization.ValidatorWalletName)
+	swapWalletAddr := chainANode.CreateWalletAndFund(walletName, []string{initialization.WalletFeeTokens.String()}, chainA)
 
 	// We add 5 ms to avoid landing directly on block time in twap. If block time
 	// is provided as start time, the latest spot price is used. Otherwise
 	// interpolation is done.
-	timeBeforeSwapPlus5ms := chainABNode.QueryLatestBlockTime().Add(5 * time.Millisecond)
+	timeBeforeSwapPlus5ms := chainANode.QueryLatestBlockTime().Add(5 * time.Millisecond)
 	s.T().Log("geometric twap, start time ", timeBeforeSwapPlus5ms.Unix())
 
 	// Wait for the next height so that the requested twap
 	// start time (timeBeforeSwap) is not equal to the block time.
-	chainAB.WaitForNumHeights(2)
+	chainA.WaitForNumHeights(2)
 
 	s.T().Log("querying for the first geometric TWAP to now (before swap)")
 	// Assume base = uosmo, quote = stake
 	// At pool creation time, the twap should be:
 	// quote assset supply / base asset supply = 2_000_000 / 1_000_000 = 2
-	curBlockTime := chainABNode.QueryLatestBlockTime().Unix()
+	curBlockTime := chainANode.QueryLatestBlockTime().Unix()
 	s.T().Log("geometric twap, end time ", curBlockTime)
 
-	initialTwapBOverA, err := chainABNode.QueryGeometricTwapToNow(poolId, denomA, denomB, timeBeforeSwapPlus5ms)
+	initialTwapBOverA, err := chainANode.QueryGeometricTwapToNow(poolId, denomA, denomB, timeBeforeSwapPlus5ms)
 	s.Require().NoError(err)
 	s.Require().Equal(osmomath.NewDec(2), initialTwapBOverA)
 
 	// Assume base = stake, quote = uosmo
 	// At pool creation time, the twap should be:
 	// quote assset supply / base asset supply = 1_000_000 / 2_000_000 = 0.5
-	initialTwapAOverB, err := chainABNode.QueryGeometricTwapToNow(poolId, denomB, denomA, timeBeforeSwapPlus5ms)
+	initialTwapAOverB, err := chainANode.QueryGeometricTwapToNow(poolId, denomB, denomA, timeBeforeSwapPlus5ms)
 	s.Require().NoError(err)
 	s.Require().Equal(osmomath.NewDecWithPrec(5, 1), initialTwapAOverB)
 
 	coinAIn := fmt.Sprintf("1000000%s", denomA)
-	chainABNode.BankSend(coinAIn, sender, swapWalletAddr)
+	chainANode.BankSend(coinAIn, sender, swapWalletAddr)
 
 	s.T().Logf("performing swap of %s for %s", coinAIn, denomB)
 
 	// stake out = stake supply * (1 - (uosmo supply before / uosmo supply after)^(uosmo weight / stake weight))
 	//           = 2_000_000 * (1 - (1_000_000 / 2_000_000)^1)
 	//           = 2_000_000 * 0.5
 	//           = 1_000_000
-	chainABNode.SwapExactAmountIn(coinAIn, minAmountOut, fmt.Sprintf("%d", poolId), denomB, swapWalletAddr)
+	chainANode.SwapExactAmountIn(coinAIn, minAmountOut, fmt.Sprintf("%d", poolId), denomB, swapWalletAddr)
 
 	// New supply post swap:
 	// stake = 2_000_000 - 1_000_000 - 1_000_000
 	// uosmo = 1_000_000 + 1_000_000 = 2_000_000
 
-	timeAfterSwap := chainABNode.QueryLatestBlockTime()
-	chainAB.WaitForNumHeights(1)
-	timeAfterSwapPlus1Height := chainABNode.QueryLatestBlockTime()
+	timeAfterSwap := chainANode.QueryLatestBlockTime()
+	chainA.WaitForNumHeights(1)
+	timeAfterSwapPlus1Height := chainANode.QueryLatestBlockTime()
 
 	s.T().Log("querying for the TWAP from after swap to now")
-	afterSwapTwapBOverA, err := chainABNode.QueryGeometricTwap(poolId, denomA, denomB, timeAfterSwap, timeAfterSwapPlus1Height)
+	afterSwapTwapBOverA, err := chainANode.QueryGeometricTwap(poolId, denomA, denomB, timeAfterSwap, timeAfterSwapPlus1Height)
 	s.Require().NoError(err)
 
 	// We swap uosmo so uosmo's supply will increase and stake will decrease.
@@ -1825,35 +1836,24 @@ func (s *IntegrationTestSuite) GeometricTWAP() {
 	osmoassert.DecApproxEq(s.T(), osmomath.NewDecWithPrec(5, 1), afterSwapTwapBOverA, osmomath.NewDecWithPrec(1, 2))
 }
 
-func (s *IntegrationTestSuite) SetDefaultTakerFeeBothChains() {
-	var wg sync.WaitGroup
-	wg.Add(2)
-
-	// Chain A
+// Only set taker fee on chain B as some tests depend on the exact swap values.
+// For example, Geometric twap. As a result, we use chain A for these tests.
+//
+// Similarly, CL tests depend on taker fee being set.
+// As a result, we deterministically configure chain B's taker fee prior to running CL tests.
+func (s *IntegrationTestSuite) SetDefaultTakerFeeChainB() {
 
-	go func() {
-		defer wg.Done()
-		chainA, chainANode, err := s.getChainACfgs()
-		s.Require().NoError(err)
-		s.SetDefaultTakerFee(chainA, chainANode)
-	}()
+	// Note: do not set taker fee on Chain A as
+	// geometric TWAP test depends on specific values that might be affected
+	// by the taker fee.
 
 	// Chain B
 
-	go func() {
-		defer wg.Done()
-		chainB, chainBNode, err := s.getChainBCfgs()
-		s.Require().NoError(err)
-		s.SetDefaultTakerFee(chainB, chainBNode)
-	}()
+	// Note: CL tests depend on taker fee being set to non-zero value.
 
-	// Wait for all goroutines to complete
-	wg.Wait()
-}
-
-func (s *IntegrationTestSuite) SetDefaultTakerFee(chain *chain.Config, chainNode *chain.NodeConfig) {
-	// Change the parameter to set the default taker fee to a non zero value
+	chainB, chainBNode, err := s.getChainBCfgs()
+	s.Require().NoError(err)
 
-	err := chainNode.ParamChangeProposal("poolmanager", string(poolmanagertypes.KeyDefaultTakerFee), json.RawMessage(`"0.001500000000000000"`), chain)
+	err = chainBNode.ParamChangeProposal("poolmanager", string(poolmanagertypes.KeyDefaultTakerFee), json.RawMessage(`"0.001500000000000000"`), chainB)
 	s.Require().NoError(err)
 }
```
