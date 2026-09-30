# [?] Merge pull request #9253 from ziggie1984/fix-chanArb-deadlock

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2024-11-20
Source: https://github.com/lightningnetwork/lnd/commit/4b563e6f495ed6442a8d0a1dd56177e75edd7cb3
Type: security-commit

## Details
Merge pull request #9253 from ziggie1984/fix-chanArb-deadlock

fix chanArb deadlock

## Patch
### contractcourt/chain_arbitrator.go
```diff
@@ -335,11 +335,10 @@ func (a *arbChannel) NewAnchorResolutions() (*lnwallet.AnchorResolutions,
 // ForceCloseChan should force close the contract that this attendant is
 // watching over. We'll use this when we decide that we need to go to chain. It
 // should in addition tell the switch to remove the corresponding link, such
-// that we won't accept any new updates. The returned summary contains all items
-// needed to eventually resolve all outputs on chain.
+// that we won't accept any new updates.
 //
 // NOTE: Part of the ArbChannel interface.
-func (a *arbChannel) ForceCloseChan() (*lnwallet.LocalForceCloseSummary, error) {
+func (a *arbChannel) ForceCloseChan() (*wire.MsgTx, error) {
 	// First, we mark the channel as borked, this ensure
 	// that no new state transitions can happen, and also
 	// that the link won't be loaded into the switch.
@@ -386,7 +385,15 @@ func (a *arbChannel) ForceCloseChan() (*lnwallet.LocalForceCloseSummary, error)
 	if err != nil {
 		return nil, err
 	}
-	return chanMachine.ForceClose()
+
+	closeSummary, err := chanMachine.ForceClose(
+		lnwallet.WithSkipContractResolutions(),
+	)
+	if err != nil {
+		return nil, err
+	}
+
+	return closeSummary.CloseTx, nil
 }
 
 // newActiveChannelArbitrator creates a new instance of an active channel
```

### contractcourt/chain_watcher.go
```diff
@@ -1175,16 +1175,29 @@ func (c *chainWatcher) dispatchLocalForceClose(
 		LocalChanConfig:         c.cfg.chanState.LocalChanCfg,
 	}
 
+	resolutions, err := forceClose.ContractResolutions.UnwrapOrErr(
+		fmt.Errorf("resolutions not found"),
+	)
+	if err != nil {
+		return err
+	}
+
 	// If our commitment output isn't dust or we have active HTLC's on the
 	// commitment transaction, then we'll populate the balances on the
 	// close channel summary.
-	if forceClose.CommitResolution != nil {
-		closeSummary.SettledBalance = chanSnapshot.LocalBalance.ToSatoshis()
-		closeSummary.TimeLockedBalance = chanSnapshot.LocalBalance.ToSatoshis()
+	if resolutions.CommitResolution != nil {
+		localBalance := chanSnapshot.LocalBalance.ToSatoshis()
+		closeSummary.SettledBalance = localBalance
+		closeSummary.TimeLockedBalance = localBalance
 	}
-	for _, htlc := range forceClose.HtlcResolutions.OutgoingHTLCs {
-		htlcValue := btcutil.Amount(htlc.SweepSignDesc.Output.Value)
-		closeSummary.TimeLockedBalance += htlcValue
+
+	if resolutions.HtlcResolutions != nil {
+		for _, htlc := range resolutions.HtlcResolutions.OutgoingHTLCs {
+			htlcValue := btcutil.Amount(
+				htlc.SweepSignDesc.Output.Value,
+			)
+			closeSummary.TimeLockedBalance += htlcValue
+		}
 	}
 
 	// Attempt to add a channel sync message to the close summary.
```

### contractcourt/chain_watcher_test.go
```diff
@@ -504,14 +504,24 @@ func TestChainWatcherLocalForceCloseDetect(t *testing.T) {
 		// outputs.
 		select {
 		case summary := <-chanEvents.LocalUnilateralClosure:
+			resOpt := summary.LocalForceCloseSummary.
+				ContractResolutions
+
+			resolutions, err := resOpt.UnwrapOrErr(
+				fmt.Errorf("resolutions not found"),
+			)
+			if err != nil {
+				t.Fatalf("unable to get resolutions: %v", err)
+			}
+
 			// Make sure we correctly extracted the commit
 			// resolution if we had a local output.
 			if remoteOutputOnly {
-				if summary.CommitResolution != nil {
+				if resolutions.CommitResolution != nil {
 					t.Fatalf("expected no commit resolution")
 				}
 			} else {
-				if summary.CommitResolution == nil {
+				if resolutions.CommitResolution == nil {
 					t.Fatalf("expected commit resolution")
 				}
 			}
```

### contractcourt/channel_arbitrator.go
```diff
@@ -98,7 +98,7 @@ type ArbChannel interface {
 	// corresponding link, such that we won't accept any new updates. The
 	// returned summary contains all items needed to eventually resolve all
 	// outputs on chain.
-	ForceCloseChan() (*lnwallet.LocalForceCloseSummary, error)
+	ForceCloseChan() (*wire.MsgTx, error)
 
 	// NewAnchorResolutions returns the anchor resolutions for currently
 	// valid commitment transactions.
@@ -1098,7 +1098,7 @@ func (c *ChannelArbitrator) stateStep(
 		// We'll tell the switch that it should remove the link for
 		// this channel, in addition to fetching the force close
 		// summary needed to close this channel on chain.
-		closeSummary, err := c.cfg.Channel.ForceCloseChan()
+		forceCloseTx, err := c.cfg.Channel.ForceCloseChan()
 		if err != nil {
 			log.Errorf("ChannelArbitrator(%v): unable to "+
 				"force close: %v", c.cfg.ChanPoint, err)
@@ -1118,7 +1118,7 @@ func (c *ChannelArbitrator) stateStep(
 
 			return StateError, closeTx, err
 		}
-		closeTx = closeSummary.CloseTx
+		closeTx = forceCloseTx
 
 		// Before publishing the transaction, we store it to the
 		// database, such that we can re-publish later in case it
@@ -2812,11 +2812,36 @@ func (c *ChannelArbitrator) channelAttendant(bestHeight int32) {
 			}
 			closeTx := closeInfo.CloseTx
 
+			resolutions, err := closeInfo.ContractResolutions.
+				UnwrapOrErr(
+					fmt.Errorf("resolutions not found"),
+				)
+			if err != nil {
+				log.Errorf("ChannelArbitrator(%v): unable to "+
+					"get resolutions: %v", c.cfg.ChanPoint,
+					err)
+
+				return
+			}
+
+			// We make sure that the htlc resolutions are present
+			// otherwise we would panic dereferencing the pointer.
+			//
+			// TODO(ziggie): Refactor ContractResolutions to use
+			// options.
+			if resolutions.HtlcResolutions == nil {
+				log.Errorf("ChannelArbitrator(%v): htlc "+
+					"resolutions not found",
+					c.cfg.ChanPoint)
+
+				return
+			}
+
 			contractRes := &ContractResolutions{
 				CommitHash:       closeTx.TxHash(),
-				CommitResolution: closeInfo.CommitResolution,
-				HtlcResolutions:  *closeInfo.HtlcResolutions,
-				AnchorResolution: closeInfo.AnchorResolution,
+				CommitResolution: resolutions.CommitResolution,
+				HtlcResolutions:  *resolutions.HtlcResolutions,
+				AnchorResolution: resolutions.AnchorResolution,
 			}
 
 			// When processing a unilateral close event, we'll
@@ -2825,7 +2850,7 @@ func (c *ChannelArbitrator) channelAttendant(bestHeight int32) {
 			// available to fetch in that state, we'll also write
 			// the commit set so we can reconstruct our chain
 			// actions on restart.
-			err := c.log.LogContractResolutions(contractRes)
+			err = c.log.LogContractResolutions(contractRes)
 			if err != nil {
 				log.Errorf("Unable to write resolutions: %v",
 					err)
```

### contractcourt/channel_arbitrator_test.go
```diff
@@ -693,11 +693,15 @@ func TestChannelArbitratorLocalForceClose(t *testing.T) {
 	chanArbCtx.AssertState(StateCommitmentBroadcasted)
 
 	// Now notify about the local force close getting confirmed.
+	//
+	//nolint:lll
 	chanArb.cfg.ChainEvents.LocalUnilateralClosure <- &LocalUnilateralCloseInfo{
 		SpendDetail: &chainntnfs.SpendDetail{},
 		LocalForceCloseSummary: &lnwallet.LocalForceCloseSummary{
-			CloseTx:         &wire.MsgTx{},
-			HtlcResolutions: &lnwallet.HtlcResolutions{},
+			CloseTx: &wire.MsgTx{},
+			ContractResolutions: fn.Some(lnwallet.ContractResolutions{
+				HtlcResolutions: &lnwallet.HtlcResolutions{},
+			}),
 		},
 		ChannelCloseSummary: &channeldb.ChannelCloseSummary{},
 	}
@@ -987,15 +991,18 @@ func TestChannelArbitratorLocalForceClosePendingHtlc(t *testing.T) {
 		},
 	}
 
+	//nolint:lll
 	chanArb.cfg.ChainEvents.LocalUnilateralClosure <- &LocalUnilateralCloseInfo{
 		SpendDetail: &chainntnfs.SpendDetail{},
 		LocalForceCloseSummary: &lnwallet.LocalForceCloseSummary{
 			CloseTx: closeTx,
-			HtlcResolutions: &lnwallet.HtlcResolutions{
-				OutgoingHTLCs: []lnwallet.OutgoingHtlcResolution{
-					outgoingRes,
+			ContractResolutions: fn.Some(lnwallet.ContractResolutions{
+				HtlcResolutions: &lnwallet.HtlcResolutions{
+					OutgoingHTLCs: []lnwallet.OutgoingHtlcResolution{
+						outgoingRes,
+					},
 				},
-			},
+			}),
 		},
 		ChannelCloseSummary: &channeldb.ChannelCloseSummary{},
 		CommitSet: CommitSet{
@@ -1613,12 +1620,15 @@ func TestChannelArbitratorCommitFailure(t *testing.T) {
 		},
 		{
 			closeType: channeldb.LocalForceClose,
+			//nolint:lll
 			sendEvent: func(chanArb *ChannelArbitrator) {
 				chanArb.cfg.ChainEvents.LocalUnilateralClosure <- &LocalUnilateralCloseInfo{
 					SpendDetail: &chainntnfs.SpendDetail{},
 					LocalForceCloseSummary: &lnwallet.LocalForceCloseSummary{
-						CloseTx:         &wire.MsgTx{},
-						HtlcResolutions: &lnwallet.HtlcResolutions{},
+						CloseTx: &wire.MsgTx{},
+						ContractResolutions: fn.Some(lnwallet.ContractResolutions{
+							HtlcResolutions: &lnwallet.HtlcResolutions{},
+						}),
 					},
 					ChannelCloseSummary: &channeldb.ChannelCloseSummary{},
 				}
@@ -1946,11 +1956,15 @@ func TestChannelArbitratorDanglingCommitForceClose(t *testing.T) {
 			// being canalled back. Also note that there're no HTLC
 			// resolutions sent since we have none on our
 			// commitment transaction.
+			//
+			//nolint:lll
 			uniCloseInfo := &LocalUnilateralCloseInfo{
 				SpendDetail: &chainntnfs.SpendDetail{},
 				LocalForceCloseSummary: &lnwallet.LocalForceCloseSummary{
-					CloseTx:         closeTx,
-					HtlcResolutions: &lnwallet.HtlcResolutions{},
+					CloseTx: closeTx,
+					ContractResolutions: fn.Some(lnwallet.ContractResolutions{
+						HtlcResolutions: &lnwallet.HtlcResolutions{},
+					}),
 				},
 				ChannelCloseSummary: &channeldb.ChannelCloseSummary{},
 				CommitSet: CommitSet{
@@ -2870,12 +2884,15 @@ func TestChannelArbitratorAnchors(t *testing.T) {
 		},
 	}
 
+	//nolint:lll
 	chanArb.cfg.ChainEvents.LocalUnilateralClosure <- &LocalUnilateralCloseInfo{
 		SpendDetail: &chainntnfs.SpendDetail{},
 		LocalForceCloseSummary: &lnwallet.LocalForceCloseSummary{
-			CloseTx:          closeTx,
-			HtlcResolutions:  &lnwallet.HtlcResolutions{},
-			AnchorResolution: anchorResolution,
+			CloseTx: closeTx,
+			ContractResolutions: fn.Some(lnwallet.ContractResolutions{
+				HtlcResolutions:  &lnwallet.HtlcResolutions{},
+				AnchorResolution: anchorResolution,
+			}),
 		},
 		ChannelCloseSummary: &channeldb.ChannelCloseSummary{},
 		CommitSet: CommitSet{
@@ -3109,14 +3126,10 @@ func (m *mockChannel) NewAnchorResolutions() (*lnwallet.AnchorResolutions,
 	return &lnwallet.AnchorResolutions{}, nil
 }
 
-func (m *mockChannel) ForceCloseChan() (*lnwallet.LocalForceCloseSummary, error) {
+func (m *mockChannel) ForceCloseChan() (*wire.MsgTx, error) {
 	if m.forceCloseErr != nil {
 		return nil, m.forceCloseErr
 	}
 
-	summary := &lnwallet.LocalForceCloseSummary{
-		CloseTx:         &wire.MsgTx{},
-		HtlcResolutions: &lnwallet.HtlcResolutions{},
-	}
-	return summary, nil
+	return &wire.MsgTx{}, nil
 }
```

### docs/release-notes/release-notes-0.19.0.md
```diff
@@ -56,6 +56,9 @@
 
 * [Fixed a case](https://github.com/lightningnetwork/lnd/pull/9258) where the
   confirmation notification may be missed.
+  
+* [Make the contract resolutions for the channel arbitrator optional](
+  https://github.com/lightningnetwork/lnd/pull/9253)
 
 # New Features
 ## Functional Enhancements
```

### lnwallet/channel.go
```diff
@@ -7852,6 +7852,18 @@ type LocalForceCloseSummary struct {
 	// commitment state.
 	CloseTx *wire.MsgTx
 
+	// ChanSnapshot is a snapshot of the final state of the channel at the
+	// time the summary was created.
+	ChanSnapshot channeldb.ChannelSnapshot
+
+	// ContractResolutions contains all the data required for resolving the
+	// different output types of a commitment transaction.
+	ContractResolutions fn.Option[ContractResolutions]
+}
+
+// ContractResolutions contains all the data required for resolving the
+// different output types of a commitment transaction.
+type ContractResolutions struct {
 	// CommitResolution contains all the data required to sweep the output
 	// to ourselves. Since this is our commitment transaction, we'll need
 	// to wait a time delay before we can sweep the output.
@@ -7860,19 +7872,38 @@ type LocalForceCloseSummary struct {
 	// then this will be nil.
 	CommitResolution *CommitOutputResolution
 
+	// AnchorResolution contains the data required to sweep the anchor
+	// output. If the channel type doesn't include anchors, the value of
+	// this field will be nil.
+	AnchorResolution *AnchorResolution
+
 	// HtlcResolutions contains all the data required to sweep any outgoing
 	// HTLC's and incoming HTLc's we know the preimage to. For each of these
 	// HTLC's, we'll need to go to the second level to sweep them fully.
 	HtlcResolutions *HtlcResolutions
+}
 
-	// ChanSnapshot is a snapshot of the final state of the channel at the
-	// time the summary was created.
-	ChanSnapshot channeldb.ChannelSnapshot
+// ForceCloseOpt is a functional option argument for the ForceClose method.
+type ForceCloseOpt func(*forceCloseConfig)
 
-	// AnchorResolution contains the data required to sweep the anchor
-	// output. If the channel type doesn't include anchors, the value of
-	// this field will be nil.
-	AnchorResolution *AnchorResolution
+// forceCloseConfig holds the configuration options for force closing a channel.
+type forceCloseConfig struct {
+	// skipResolution if true will skip creating the contract resolutions
+	// when generating the force close summary.
+	skipResolution bool
+}
+
+// defaultForceCloseConfig returns the default force close configuration.
+func defaultForceCloseConfig() *forceCloseConfig {
+	return &forceCloseConfig{}
+}
+
+// WithSkipContractResolutions creates an option to skip the contract
+// resolutions from the returned summary.
+func WithSkipContractResolutions() ForceCloseOpt {
+	return func(cfg *forceCloseConfig) {
+		cfg.skipResolution = true
+	}
 }
 
 // ForceClose executes a unilateral closure of the transaction at the current
@@ -7883,10 +7914,17 @@ type LocalForceCloseSummary struct {
 // outputs within the commitment transaction.
 //
 // TODO(roasbeef): all methods need to abort if in dispute state
-func (lc *LightningChannel) ForceClose() (*LocalForceCloseSummary, error) {
+func (lc *LightningChannel) ForceClose(opts ...ForceCloseOpt) (
+	*LocalForceCloseSummary, error) {
+
 	lc.Lock()
 	defer lc.Unlock()
 
+	cfg := defaultForceCloseConfig()
+	for _, opt := range opts {
+		opt(cfg)
+	}
+
 	// If we've detected local data loss for this channel, then we won't
 	// allow a force close, as it may be the case that we have a dated
 	// version of the commitment, or this is actually a channel shell.
@@ -7901,6 +7939,14 @@ func (lc *LightningChannel) ForceClose() (*LocalForceCloseSummary, error) {
 		return nil, err
 	}
 
+	if cfg.skipResolution {
+		return &LocalForceCloseSummary{
+			ChanPoint:    lc.channelState.FundingOutpoint,
+			ChanSnapshot: *lc.channelState.Snapshot(),
+			CloseTx:      commitTx,
+		}, nil
+	}
+
 	localCommitment := lc.channelState.LocalCommitment
 	summary, err := NewLocalForceCloseSummary(
 		lc.channelState, lc.Signer, commitTx,
@@ -8107,12 +8153,14 @@ func NewLocalForceCloseSummary(chanState *channeldb.OpenChannel,
 	}
 
 	return &LocalForceCloseSummary{
-		ChanPoint:        chanState.FundingOutpoint,
-		CloseTx:          commitTx,
-		CommitResolution: commitResolution,
-		HtlcResolutions:  htlcResolutions,
-		ChanSnapshot:     *chanState.Snapshot(),
-		AnchorResolution: anchorResolution,
+		ChanPoint:    chanState.FundingOutpoint,
+		CloseTx:      commitTx,
+		ChanSnapshot: *chanState.Snapshot(),
+		ContractResolutions: fn.Some(ContractResolutions{
+			CommitResolution: commitResolution,
+			HtlcResolutions:  htlcResolutions,
+			AnchorResolution: anchorResolution,
+		}),
 	}, nil
 }
 
```

### lnwallet/channel_test.go
```diff
@@ -959,24 +959,26 @@ func testForceClose(t *testing.T, testCase *forceCloseTestCase) {
 	closeSummary, err := aliceChannel.ForceClose()
 	require.NoError(t, err, "unable to force close channel")
 
+	resolutionsAlice := closeSummary.ContractResolutions.UnwrapOrFail(t)
+
 	// Alice should detect that she can sweep the outgoing HTLC after a
 	// timeout, but also that she's able to sweep in incoming HTLC Bob sent
 	// her.
-	if len(closeSummary.HtlcResolutions.OutgoingHTLCs) != 1 {
+	if len(resolutionsAlice.HtlcResolutions.OutgoingHTLCs) != 1 {
 		t.Fatalf("alice out htlc resolutions not populated: expected %v "+
 			"htlcs, got %v htlcs",
-			1, len(closeSummary.HtlcResolutions.OutgoingHTLCs))
+			1, len(resolutionsAlice.HtlcResolutions.OutgoingHTLCs))
 	}
-	if len(closeSummary.HtlcResolutions.IncomingHTLCs) != 1 {
+	if len(resolutionsAlice.HtlcResolutions.IncomingHTLCs) != 1 {
 		t.Fatalf("alice in htlc resolutions not populated: expected %v "+
 			"htlcs, got %v htlcs",
-			1, len(closeSummary.HtlcResolutions.IncomingHTLCs))
+			1, len(resolutionsAlice.HtlcResolutions.IncomingHTLCs))
 	}
 
 	// Verify the anchor resolutions for the anchor commitment format.
 	if testCase.chanType.HasAnchors() {
 		// Check the close summary resolution.
-		anchorRes := closeSummary.AnchorResolution
+		anchorRes := resolutionsAlice.AnchorResolution
 		if anchorRes == nil {
 			t.Fatal("expected anchor resolution")
 		}
@@ -1010,7 +1012,7 @@ func testForceClose(t *testing.T, testCase *forceCloseTestCase) {
 
 	// The SelfOutputSignDesc should be non-nil since the output to-self is
 	// non-dust.
-	aliceCommitResolution := closeSummary.CommitResolution
+	aliceCommitResolution := resolutionsAlice.CommitResolution
 	if aliceCommitResolution == nil {
 		t.Fatalf("alice fails to include to-self output in " +
 			"ForceCloseSummary")
@@ -1056,7 +1058,7 @@ func testForceClose(t *testing.T, testCase *forceCloseTestCase) {
 	// Next, we'll ensure that the second level HTLC transaction it itself
 	// spendable, and also that the delivery output (with delay) itself has
 	// a valid sign descriptor.
-	htlcResolution := closeSummary.HtlcResolutions.OutgoingHTLCs[0]
+	htlcResolution := resolutionsAlice.HtlcResolutions.OutgoingHTLCs[0]
 	outHtlcIndex := htlcResolution.SignedTimeoutTx.TxIn[0].PreviousOutPoint.Index
 	senderHtlcPkScript := closeSummary.CloseTx.TxOut[outHtlcIndex].PkScript
 
@@ -1140,7 +1142,7 @@ func testForceClose(t *testing.T, testCase *forceCloseTestCase) {
 	// We'll now perform similar set of checks to ensure that Alice is able
 	// to sweep the output that Bob sent to her on-chain with knowledge of
 	// the preimage.
-	inHtlcResolution := closeSummary.HtlcResolutions.IncomingHTLCs[0]
+	inHtlcResolution := resolutionsAlice.HtlcResolutions.IncomingHTLCs[0]
 	inHtlcIndex := inHtlcResolution.SignedSuccessTx.TxIn[0].PreviousOutPoint.Index
 	receiverHtlcScript := closeSummary.CloseTx.TxOut[inHtlcIndex].PkScript
 
@@ -1221,7 +1223,8 @@ func testForceClose(t *testing.T, testCase *forceCloseTestCase) {
 	// Check the same for Bob's ForceCloseSummary.
 	closeSummary, err = bobChannel.ForceClose()
 	require.NoError(t, err, "unable to force close channel")
-	bobCommitResolution := closeSummary.CommitResolution
+	resolutionsBob := closeSummary.ContractResolutions.UnwrapOrFail(t)
+	bobCommitResolution := resolutionsBob.CommitResolution
 	if bobCommitResolution == nil {
 		t.Fatalf("bob fails to include to-self output in ForceCloseSummary")
 	}
@@ -1255,19 +1258,19 @@ func testForceClose(t *testing.T, testCase *forceCloseTestCase) {
 	// As we didn't add the preimage of Alice's HTLC to bob's preimage
 	// cache, he should only detect that he can sweep only his outgoing
 	// HTLC upon force close.
-	if len(closeSummary.HtlcResolutions.OutgoingHTLCs) != 1 {
+	if len(resolutionsBob.HtlcResolutions.OutgoingHTLCs) != 1 {
 		t.Fatalf("alice out htlc resolutions not populated: expected %v "+
 			"htlcs, got %v htlcs",
-			1, len(closeSummary.HtlcResolutions.OutgoingHTLCs))
+			1, len(resolutionsBob.HtlcResolutions.OutgoingHTLCs))
 	}
 
 	// Bob should recognize that the incoming HTLC is there, but the
 	// preimage should be empty as he doesn't have the knowledge required
 	// to sweep it.
-	if len(closeSummary.HtlcResolutions.IncomingHTLCs) != 1 {
+	if len(resolutionsBob.HtlcResolutions.IncomingHTLCs) != 1 {
 		t.Fatalf("bob in htlc resolutions not populated: expected %v "+
 			"htlcs, got %v htlcs",
-			1, len(closeSummary.HtlcResolutions.IncomingHTLCs))
+			1, len(resolutionsBob.HtlcResolutions.IncomingHTLCs))
 	}
 }
 
@@ -1326,9 +1329,11 @@ func TestForceCloseDustOutput(t *testing.T) {
 	closeSummary, err := aliceChannel.ForceClose()
 	require.NoError(t, err, "unable to force close channel")
 
+	resolutionsAlice := closeSummary.ContractResolutions.UnwrapOrFail(t)
+
 	// Alice's to-self output should still be in the commitment
 	// transaction.
-	commitResolution := closeSummary.CommitResolution
+	commitResolution := resolutionsAlice.CommitResolution
 	if commitResolution == nil {
 		t.Fatalf("alice fails to include to-self output in " +
 			"ForceCloseSummary")
@@ -1362,10 +1367,11 @@ func TestForceCloseDustOutput(t *testing.T) {
 
 	closeSummary, err = bobChannel.ForceClose()
 	require.NoError(t, err, "unable to force close channel")
+	resolutionsBob := closeSummary.ContractResolutions.UnwrapOrFail(t)
 
 	// Bob's to-self output is below Bob's dust value and should be
 	// reflected in the ForceCloseSummary.
-	commitResolution = closeSummary.CommitResolution
+	commitResolution = resolutionsBob.CommitResolution
 	if commitResolution != nil {
 		t.Fatalf("bob incorrectly includes to-self output in " +
 			"ForceCloseSummary")
```

### lnwallet/transactions_test.go
```diff
@@ -406,6 +406,8 @@ func testVectors(t *testing.T, chanType channeldb.ChannelType, test testCase) {
 		hex.EncodeToString(txBytes.Bytes()),
 	)
 
+	resolutions := forceCloseSum.ContractResolutions.UnwrapOrFail(t)
+
 	// Obtain the second level transactions that the local node's channel
 	// state machine has produced. Store them in a map indexed by commit tx
 	// output index. Also complete the second level transaction with the
@@ -419,7 +421,8 @@ func testVectors(t *testing.T, chanType channeldb.ChannelType, test testCase) {
 		secondLevelTxes[index] = tx
 	}
 
-	for _, r := range forceCloseSum.HtlcResolutions.IncomingHTLCs {
+	htlcResolutions := resolutions.HtlcResolutions
+	for _, r := range htlcResolutions.IncomingHTLCs {
 		successTx := r.SignedSuccessTx
 		witnessScript := successTx.TxIn[0].Witness[4]
 		var hash160 [20]byte
@@ -428,7 +431,7 @@ func testVectors(t *testing.T, chanType channeldb.ChannelType, test testCase) {
 		successTx.TxIn[0].Witness[3] = preimage[:]
 		storeTx(r.HtlcPoint().Index, successTx)
 	}
-	for _, r := range forceCloseSum.HtlcResolutions.OutgoingHTLCs {
+	for _, r := range htlcResolutions.OutgoingHTLCs {
 		storeTx(r.HtlcPoint().Index, r.SignedTimeoutTx)
 	}
 
```

### rpcserver.go
```diff
@@ -2739,6 +2739,14 @@ func (r *rpcServer) CloseChannel(in *lnrpc.CloseChannelRequest,
 			return err
 		}
 
+		// Safety check which should never happen.
+		//
+		// TODO(ziggie): remove pointer as return value from
+		// ForceCloseContract.
+		if closingTx == nil {
+			return fmt.Errorf("force close transaction is nil")
+		}
+
 		closingTxid := closingTx.TxHash()
 
 		// With the transaction broadcast, we send our first update to
```
