# [?] go/keymanager/churp: Fix handoff epoch overflows

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2024-05-08
Source: https://github.com/oasisprotocol/oasis-core/commit/c67a315ca9b85921ac17eacc7a7bfe9860889664
Type: security-commit

## Details
go/keymanager/churp: Fix handoff epoch overflows

## Patch
### go/consensus/cometbft/apps/keymanager/churp/txs.go
```diff
@@ -439,10 +439,6 @@ func addStakeClaim(ctx *tmapi.Context, entityID signature.PublicKey, runtimeID c
 	}
 
 	entityAddr := staking.NewAddress(entityID)
-	if err != nil {
-		return err
-	}
-
 	claim := churp.StakeClaim(runtimeID, churpID)
 	thresholds := churp.StakeThresholds()
 
@@ -517,19 +513,30 @@ func tryFinalizeHandoff(status *churp.Status, epochChange bool) bool {
 		return false
 	})
 
+	// Compute the next handoff epoch.
+	nextHandoff := churp.HandoffsDisabled
+	if status.Handoff < churp.HandoffsDisabled-status.HandoffInterval {
+		nextHandoff = status.NextHandoff + status.HandoffInterval
+	}
+
+	// Give nodes an extra epoch for application submission.
+	if epochChange && status.HandoffInterval == 1 && nextHandoff < churp.HandoffsDisabled {
+		nextHandoff++
+	}
+
+	// Disable handoffs when overflow happens.
+	if nextHandoff == churp.HandoffsDisabled {
+		status.HandoffInterval = 0
+	}
+
 	// Update fields.
 	status.Handoff = status.NextHandoff
 	status.Checksum = status.NextChecksum
 	status.Committee = committee
-	status.NextHandoff = status.Handoff + status.HandoffInterval
+	status.NextHandoff = nextHandoff
 	status.NextChecksum = nil
 	status.Applications = nil
 
-	// Give nodes an extra epoch for application submission.
-	if epochChange && status.HandoffInterval == 1 {
-		status.NextHandoff++
-	}
-
 	return true
 }
 
```

### go/consensus/cometbft/apps/keymanager/churp/txs_test.go
```diff
@@ -400,29 +400,29 @@ func (s *TxTestSuite) TestApply() {
 	s.create()
 
 	s.Run("not key manager runtime", func() {
-		req := s.signedApplicationRequest()
+		req := s.signedApplicationRequest(1)
 		req.Application.Identity.RuntimeID = s.computeRuntimes[0].ID
 
 		err := s.ext.apply(s.txCtx, &req)
 		require.ErrorContains(s.T(), err, "runtime is not a key manager")
 	})
 
 	s.Run("non-existing instance", func() {
-		req := s.signedApplicationRequest()
+		req := s.signedApplicationRequest(1)
 		req.Application.Identity.ID = 1 // Wrong ID.
 
 		err := s.ext.apply(s.txCtx, &req)
 		require.ErrorContains(s.T(), err, "non-existing ID")
 
-		req = s.signedApplicationRequest()
+		req = s.signedApplicationRequest(1)
 		req.Application.Identity.RuntimeID = s.keymanagerRuntimes[1].ID // Wrong runtime ID.
 
 		err = s.ext.apply(s.txCtx, &req)
 		require.ErrorContains(s.T(), err, "non-existing ID")
 	})
 
 	s.Run("handoffs disabled", func() {
-		req := s.signedApplicationRequest()
+		req := s.signedApplicationRequest(1)
 
 		err := s.ext.apply(s.txCtx, &req)
 		require.ErrorContains(s.T(), err, "handoffs disabled")
@@ -433,7 +433,7 @@ func (s *TxTestSuite) TestApply() {
 	s.cfg.CurrentEpoch = 1
 
 	s.Run("submissions closed", func() {
-		req := s.signedApplicationRequest()
+		req := s.signedApplicationRequest(1)
 
 		err := s.ext.apply(s.txCtx, &req)
 		require.ErrorContains(s.T(), err, "submissions closed")
@@ -442,15 +442,14 @@ func (s *TxTestSuite) TestApply() {
 	s.cfg.CurrentEpoch = 0
 
 	s.Run("invalid handoff epoch", func() {
-		req := s.signedApplicationRequest()
-		req.Application.Epoch = 100
+		req := s.signedApplicationRequest(100)
 
 		err := s.ext.apply(s.txCtx, &req)
 		require.ErrorContains(s.T(), err, "invalid handoff")
 	})
 
 	s.Run("invalid RAK signature", func() {
-		req := s.signedApplicationRequest()
+		req := s.signedApplicationRequest(1)
 
 		s.txCtx.SetTxSigner(s.nodes[0].signer.Public())
 
@@ -459,7 +458,7 @@ func (s *TxTestSuite) TestApply() {
 	})
 
 	s.Run("happy path", func() {
-		req := s.signedApplicationRequest()
+		req := s.signedApplicationRequest(1)
 		s.signApplicationRequest(0, &req)
 
 		s.txCtx.SetTxSigner(s.nodes[0].signer.Public())
@@ -469,7 +468,7 @@ func (s *TxTestSuite) TestApply() {
 	})
 
 	s.Run("duplicate submission", func() {
-		req := s.signedApplicationRequest()
+		req := s.signedApplicationRequest(1)
 		s.signApplicationRequest(0, &req)
 
 		err := s.ext.apply(s.txCtx, &req)
@@ -481,29 +480,29 @@ func (s *TxTestSuite) TestConfirm() {
 	s.create()
 
 	s.Run("not key manager runtime", func() {
-		req := s.signedConfirmationRequest()
+		req := s.signedConfirmationRequest(1)
 		req.Confirmation.Identity.RuntimeID = s.computeRuntimes[0].ID
 
 		err := s.ext.confirm(s.txCtx, &req)
 		require.ErrorContains(s.T(), err, "runtime is not a key manager")
 	})
 
 	s.Run("non-existing instance", func() {
-		req := s.signedConfirmationRequest() // Wrong ID.
+		req := s.signedConfirmationRequest(1) // Wrong ID.
 		req.Confirmation.Identity.ID = 1
 
 		err := s.ext.confirm(s.txCtx, &req)
 		require.ErrorContains(s.T(), err, "non-existing ID")
 
-		req = s.signedConfirmationRequest()
+		req = s.signedConfirmationRequest(1)
 		req.Confirmation.Identity.RuntimeID = s.keymanagerRuntimes[1].ID // Wrong runtime ID.
 
 		err = s.ext.confirm(s.txCtx, &req)
 		require.ErrorContains(s.T(), err, "non-existing ID")
 	})
 
 	s.Run("handoffs disabled", func() {
-		req := s.signedConfirmationRequest()
+		req := s.signedConfirmationRequest(1)
 
 		err := s.ext.confirm(s.txCtx, &req)
 		require.ErrorContains(s.T(), err, "handoffs disabled")
@@ -514,7 +513,7 @@ func (s *TxTestSuite) TestConfirm() {
 	s.cfg.CurrentEpoch = 2
 
 	s.Run("confirmations closed", func() {
-		req := s.signedConfirmationRequest()
+		req := s.signedConfirmationRequest(1)
 
 		err := s.ext.confirm(s.txCtx, &req)
 		require.ErrorContains(s.T(), err, "confirmations closed")
@@ -523,44 +522,32 @@ func (s *TxTestSuite) TestConfirm() {
 	s.cfg.CurrentEpoch = 1
 
 	s.Run("invalid handoff epoch", func() {
-		req := s.signedConfirmationRequest()
-		req.Confirmation.Epoch = 100
+		req := s.signedConfirmationRequest(100)
 
 		err := s.ext.confirm(s.txCtx, &req)
 		require.ErrorContains(s.T(), err, "invalid handoff")
 	})
 
 	s.Run("no application", func() {
-		req := s.signedConfirmationRequest()
+		req := s.signedConfirmationRequest(1)
 
 		err := s.ext.confirm(s.txCtx, &req)
 		require.ErrorContains(s.T(), err, "application not found")
 	})
 
 	s.cfg.CurrentEpoch = 0
-
-	// Prepare and submit few applications.
-	for i := range s.nodes {
-		req := s.signedApplicationRequest()
-		s.signApplicationRequest(i, &req)
-
-		s.txCtx.SetTxSigner(s.nodes[i].signer.Public())
-
-		err := s.ext.apply(s.txCtx, &req)
-		require.NoError(s.T(), err)
-	}
-
+	s.submitApplications(1)
 	s.cfg.CurrentEpoch = 1
 
 	s.Run("invalid RAK signature", func() {
-		req := s.signedConfirmationRequest()
+		req := s.signedConfirmationRequest(1)
 
 		err := s.ext.confirm(s.txCtx, &req)
 		require.ErrorContains(s.T(), err, "RAK signature verification failed")
 	})
 
 	s.Run("happy path", func() {
-		req := s.signedConfirmationRequest()
+		req := s.signedConfirmationRequest(1)
 		s.signConfirmationRequest(0, &req)
 
 		s.txCtx.SetTxSigner(s.nodes[0].signer.Public())
@@ -570,15 +557,15 @@ func (s *TxTestSuite) TestConfirm() {
 	})
 
 	s.Run("duplicate submission", func() {
-		req := s.signedConfirmationRequest()
+		req := s.signedConfirmationRequest(1)
 		s.signConfirmationRequest(0, &req)
 
 		err := s.ext.confirm(s.txCtx, &req)
 		require.ErrorContains(s.T(), err, "confirmation already submitted")
 	})
 
 	s.Run("checksum mismatch", func() {
-		req := s.signedConfirmationRequest()
+		req := s.signedConfirmationRequest(1)
 		req.Confirmation.Checksum = hash.Hash{3, 2, 1}
 
 		s.txCtx.SetTxSigner(s.nodes[1].signer.Public())
@@ -588,7 +575,7 @@ func (s *TxTestSuite) TestConfirm() {
 	})
 
 	s.Run("handoff completed", func() {
-		req := s.signedConfirmationRequest()
+		req := s.signedConfirmationRequest(1)
 		s.signConfirmationRequest(1, &req)
 
 		err := s.ext.confirm(s.txCtx, &req)
@@ -606,6 +593,42 @@ func (s *TxTestSuite) TestConfirm() {
 		require.Nil(s.T(), status.NextChecksum)
 		require.Nil(s.T(), status.Applications)
 	})
+
+	s.Run("handoff epoch overflow", func() {
+		// Update handoff interval to a very large number.
+		s.updateHandoffInterval(churp.HandoffsDisabled)
+
+		// Finalize handoff.
+		s.submitApplications(2)
+		s.cfg.CurrentEpoch = 2
+		s.submitConfirmations(2)
+
+		// Verify status.
+		status, err := s.state.Status(s.txCtx, s.keymanagerRuntimes[0].ID, 0)
+		require.NoError(s.T(), err)
+		require.Equal(s.T(), beacon.EpochTime(2), status.Handoff)
+		require.Equal(s.T(), churp.HandoffsDisabled, status.NextHandoff)
+		require.Equal(s.T(), beacon.EpochTime(0), status.HandoffInterval)
+		require.Nil(s.T(), status.NextChecksum)
+		require.Nil(s.T(), status.Applications)
+
+		// Lower handoff interval and try again.
+		s.updateHandoffInterval(5)
+
+		// Finalize handoff.
+		s.submitApplications(3)
+		s.cfg.CurrentEpoch = 3
+		s.submitConfirmations(3)
+
+		// Verify status.
+		status, err = s.state.Status(s.txCtx, s.keymanagerRuntimes[0].ID, 0)
+		require.NoError(s.T(), err)
+		require.Equal(s.T(), beacon.EpochTime(3), status.Handoff)
+		require.Equal(s.T(), beacon.EpochTime(8), status.NextHandoff)
+		require.Equal(s.T(), beacon.EpochTime(5), status.HandoffInterval)
+		require.Nil(s.T(), status.NextChecksum)
+		require.Nil(s.T(), status.Applications)
+	})
 }
 
 func (s *TxTestSuite) create() {
@@ -662,28 +685,28 @@ func (s *TxTestSuite) signConfirmationRequest(nodeIdx int, req *churp.SignedConf
 	copy(req.Signature[:], rawSigBytes)
 }
 
-func (s *TxTestSuite) signedApplicationRequest() churp.SignedApplicationRequest {
+func (s *TxTestSuite) signedApplicationRequest(epoch beacon.EpochTime) churp.SignedApplicationRequest {
 	return churp.SignedApplicationRequest{
 		Application: churp.ApplicationRequest{
 			Identity: churp.Identity{
 				ID:        0,
 				RuntimeID: s.keymanagerRuntimes[0].ID,
 			},
-			Epoch:    1,
+			Epoch:    epoch,
 			Checksum: hash.Hash{1, 2, 3},
 		},
 		Signature: signature.RawSignature{},
 	}
 }
 
-func (s *TxTestSuite) signedConfirmationRequest() churp.SignedConfirmationRequest {
+func (s *TxTestSuite) signedConfirmationRequest(epoch beacon.EpochTime) churp.SignedConfirmationRequest {
 	return churp.SignedConfirmationRequest{
 		Confirmation: churp.ConfirmationRequest{
 			Identity: churp.Identity{
 				ID:        0,
 				RuntimeID: s.keymanagerRuntimes[0].ID,
 			},
-			Epoch:    1,
+			Epoch:    epoch,
 			Checksum: hash.Hash{1, 2, 3},
 		},
 		Signature: signature.RawSignature{},
@@ -718,3 +741,37 @@ func (s *TxTestSuite) createRequest(id uint8) churp.CreateRequest {
 		Policy:          policy,
 	}
 }
+
+func (s *TxTestSuite) submitApplications(epoch beacon.EpochTime) {
+	for i := range s.nodes {
+		req := s.signedApplicationRequest(epoch)
+		s.signApplicationRequest(i, &req)
+
+		s.txCtx.SetTxSigner(s.nodes[i].signer.Public())
+
+		err := s.ext.apply(s.txCtx, &req)
+		require.NoError(s.T(), err)
+	}
+}
+
+func (s *TxTestSuite) submitConfirmations(epoch beacon.EpochTime) {
+	for i := range s.nodes {
+		req := s.signedConfirmationRequest(epoch)
+		s.signConfirmationRequest(i, &req)
+
+		s.txCtx.SetTxSigner(s.nodes[i].signer.Public())
+
+		err := s.ext.confirm(s.txCtx, &req)
+		require.NoError(s.T(), err)
+	}
+}
+
+func (s *TxTestSuite) updateHandoffInterval(interval beacon.EpochTime) {
+	req := s.updateRequest()
+	req.HandoffInterval = &interval
+
+	s.txCtx.SetTxSigner(s.entity.signer.Public())
+
+	err := s.ext.update(s.txCtx, &req)
+	require.NoError(s.T(), err)
+}
```
