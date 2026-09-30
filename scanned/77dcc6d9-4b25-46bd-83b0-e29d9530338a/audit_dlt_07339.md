# [?] node/pkg/solana: fix s.logger data race

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2021-09-29
Source: https://github.com/wormhole-foundation/wormhole/commit/6e4d5780416ca6932a09f270930ec0ccc99cc4d3
Type: security-commit

## Details
node/pkg/solana: fix s.logger data race

Surfaced by the retry code:
https://gist.github.com/leoluk/b5d05ed27269b077b834eda771a50058

Accessing s.logger from a goroutine will cause a data race. We didn't
previously encounter this since supervisor would wait for Run() to
return before rescheduling it.

Change-Id: I56a7503081485e58975103d0e25e0c2baf19ca08

## Patch
### node/pkg/solana/client.go
```diff
@@ -26,7 +26,6 @@ type SolanaWatcher struct {
 	rpcUrl       string
 	commitment   rpc.CommitmentType
 	messageEvent chan *common.MessagePublication
-	logger       *zap.Logger
 	rpcClient    *rpc.Client
 }
 
@@ -116,7 +115,7 @@ func (s *SolanaWatcher) Run(ctx context.Context) error {
 		ContractAddress: contractAddr,
 	})
 
-	s.logger = supervisor.Logger(ctx)
+	logger := supervisor.Logger(ctx)
 	errC := make(chan error)
 	var lastSlot uint64
 
@@ -134,13 +133,13 @@ func (s *SolanaWatcher) Run(ctx context.Context) error {
 				if s.commitment != rpc.CommitmentFinalized {
 					continue
 				}
-				s.logger.Info("executing scheduled recovery", zap.Any("accounts", recoveryAccounts))
+				logger.Info("executing scheduled recovery", zap.Any("accounts", recoveryAccounts))
 
 				rCtx, cancel := context.WithTimeout(ctx, rpcTimeout)
 				defer cancel()
 
 				for _, acc := range recoveryAccounts {
-					s.fetchMessageAccount(rCtx, solana.MustPublicKeyFromBase58(acc), 0)
+					s.fetchMessageAccount(rCtx, logger, solana.MustPublicKeyFromBase58(acc), 0)
 				}
 			case <-timer.C:
 				// Get current slot height
@@ -164,7 +163,7 @@ func (s *SolanaWatcher) Run(ctx context.Context) error {
 					Height:          int64(slot),
 					ContractAddress: contractAddr,
 				})
-				s.logger.Info("fetched current Solana height",
+				logger.Info("fetched current Solana height",
 					zap.String("commitment", string(s.commitment)),
 					zap.Uint64("slot", slot),
 					zap.Uint64("lastSlot", lastSlot),
@@ -189,7 +188,7 @@ func (s *SolanaWatcher) Run(ctx context.Context) error {
 					return
 				}
 
-				s.logger.Info("fetched slots in range",
+				logger.Info("fetched slots in range",
 					zap.Uint64("from", rangeStart), zap.Uint64("to", rangeEnd),
 					zap.Duration("took", time.Since(start)),
 					zap.String("commitment", string(s.commitment)))
@@ -202,7 +201,7 @@ func (s *SolanaWatcher) Run(ctx context.Context) error {
 						continue
 					}
 
-					go s.retryFetchBlock(ctx, slot, 0)
+					go s.retryFetchBlock(ctx, logger, slot, 0)
 				}
 
 				lastSlot = slot
@@ -218,12 +217,12 @@ func (s *SolanaWatcher) Run(ctx context.Context) error {
 	}
 }
 
-func (s *SolanaWatcher) retryFetchBlock(ctx context.Context, slot uint64, retry uint) {
-	ok := s.fetchBlock(ctx, slot)
+func (s *SolanaWatcher) retryFetchBlock(ctx context.Context, logger *zap.Logger, slot uint64, retry uint) {
+	ok := s.fetchBlock(ctx, logger, slot)
 
 	if !ok {
 		if retry >= maxRetries {
-			s.logger.Error("max retries for block",
+			logger.Error("max retries for block",
 				zap.Uint64("slot", slot),
 				zap.String("commitment", string(s.commitment)),
 				zap.Uint("retry", retry))
@@ -232,17 +231,17 @@ func (s *SolanaWatcher) retryFetchBlock(ctx context.Context, slot uint64, retry
 
 		time.Sleep(5 * time.Second)
 
-		s.logger.Info("retrying block",
+		logger.Info("retrying block",
 			zap.Uint64("slot", slot),
 			zap.String("commitment", string(s.commitment)),
 			zap.Uint("retry", retry))
 
-		go s.retryFetchBlock(ctx, slot, retry + 1)
+		go s.retryFetchBlock(ctx, logger, slot, retry+1)
 	}
 }
 
-func (s *SolanaWatcher) fetchBlock(ctx context.Context, slot uint64) bool {
-	s.logger.Debug("requesting block", zap.Uint64("slot", slot), zap.String("commitment", string(s.commitment)))
+func (s *SolanaWatcher) fetchBlock(ctx context.Context, logger *zap.Logger, slot uint64) bool {
+	logger.Debug("requesting block", zap.Uint64("slot", slot), zap.String("commitment", string(s.commitment)))
 	rCtx, cancel := context.WithTimeout(ctx, rpcTimeout)
 	defer cancel()
 	start := time.Now()
@@ -258,20 +257,20 @@ func (s *SolanaWatcher) fetchBlock(ctx context.Context, slot uint64) bool {
 	if err != nil {
 		p2p.DefaultRegistry.AddErrorCount(vaa.ChainIDSolana, 1)
 		solanaConnectionErrors.WithLabelValues(string(s.commitment), "get_confirmed_block_error").Inc()
-		s.logger.Error("failed to request block", zap.Error(err), zap.Uint64("slot", slot),
+		logger.Error("failed to request block", zap.Error(err), zap.Uint64("slot", slot),
 			zap.String("commitment", string(s.commitment)))
 		return false
 	}
 
 	if out == nil {
 		solanaConnectionErrors.WithLabelValues(string(s.commitment), "get_confirmed_block_error").Inc()
-		s.logger.Error("nil response when requesting block", zap.Error(err), zap.Uint64("slot", slot),
+		logger.Error("nil response when requesting block", zap.Error(err), zap.Uint64("slot", slot),
 			zap.String("commitment", string(s.commitment)))
 		p2p.DefaultRegistry.AddErrorCount(vaa.ChainIDSolana, 1)
 		return false
 	}
 
-	s.logger.Info("fetched block",
+	logger.Info("fetched block",
 		zap.Uint64("slot", slot),
 		zap.Int("num_tx", len(out.Transactions)),
 		zap.Duration("took", time.Since(start)),
@@ -290,16 +289,16 @@ OUTER:
 			continue
 		}
 
-		s.logger.Info("found Wormhole transaction",
+		logger.Info("found Wormhole transaction",
 			zap.Stringer("signature", signature),
 			zap.Uint64("slot", slot),
 			zap.String("commitment", string(s.commitment)))
 
 		// Find top-level instructions
 		for _, inst := range tx.Transaction.Message.Instructions {
-			found, err := s.processInstruction(ctx, slot, inst, programIndex, tx)
+			found, err := s.processInstruction(ctx, logger, slot, inst, programIndex, tx)
 			if err != nil {
-				s.logger.Error("malformed Wormhole instruction",
+				logger.Error("malformed Wormhole instruction",
 					zap.Error(err),
 					zap.Stringer("signature", signature),
 					zap.Uint64("slot", slot),
@@ -324,25 +323,25 @@ OUTER:
 		if err != nil {
 			p2p.DefaultRegistry.AddErrorCount(vaa.ChainIDSolana, 1)
 			solanaConnectionErrors.WithLabelValues(string(s.commitment), "get_confirmed_transaction_error").Inc()
-			s.logger.Error("failed to request transaction",
+			logger.Error("failed to request transaction",
 				zap.Error(err),
 				zap.Uint64("slot", slot),
 				zap.String("commitment", string(s.commitment)),
 				zap.Stringer("signature", signature))
 			return false
 		}
 
-		s.logger.Info("fetched transaction",
+		logger.Info("fetched transaction",
 			zap.Uint64("slot", slot),
 			zap.String("commitment", string(s.commitment)),
 			zap.Stringer("signature", signature),
 			zap.Duration("took", time.Since(start)))
 
 		for _, inner := range tr.Meta.InnerInstructions {
 			for _, inst := range inner.Instructions {
-				_, err := s.processInstruction(ctx, slot, inst, programIndex, tx)
+				_, err := s.processInstruction(ctx, logger, slot, inst, programIndex, tx)
 				if err != nil {
-					s.logger.Error("malformed Wormhole instruction",
+					logger.Error("malformed Wormhole instruction",
 						zap.Error(err),
 						zap.Stringer("signature", signature),
 						zap.Uint64("slot", slot),
@@ -355,7 +354,7 @@ OUTER:
 	return true
 }
 
-func (s *SolanaWatcher) processInstruction(ctx context.Context, slot uint64, inst solana.CompiledInstruction, programIndex uint16, tx rpc.TransactionWithMeta) (bool, error) {
+func (s *SolanaWatcher) processInstruction(ctx context.Context, logger *zap.Logger, slot uint64, inst solana.CompiledInstruction, programIndex uint16, tx rpc.TransactionWithMeta) (bool, error) {
 	if inst.ProgramIDIndex != programIndex {
 		return false, nil
 	}
@@ -375,7 +374,7 @@ func (s *SolanaWatcher) processInstruction(ctx context.Context, slot uint64, ins
 		return false, fmt.Errorf("failed to deserialize instruction data: %w", err)
 	}
 
-	s.logger.Info("post message data", zap.Any("deserialized_data", data))
+	logger.Info("post message data", zap.Any("deserialized_data", data))
 
 	level, err := data.ConsistencyLevel.Commitment()
 	if err != nil {
@@ -388,12 +387,12 @@ func (s *SolanaWatcher) processInstruction(ctx context.Context, slot uint64, ins
 
 	// The second account in a well-formed Wormhole instruction is the VAA program account.
 	acc := tx.Transaction.Message.AccountKeys[inst.Accounts[1]]
-	go s.fetchMessageAccount(ctx, acc, slot)
+	go s.fetchMessageAccount(ctx, logger, acc, slot)
 
 	return true, nil
 }
 
-func (s *SolanaWatcher) fetchMessageAccount(ctx context.Context, acc solana.PublicKey, slot uint64) {
+func (s *SolanaWatcher) fetchMessageAccount(ctx context.Context, logger *zap.Logger, acc solana.PublicKey, slot uint64) {
 	// Fetching account
 	rCtx, cancel := context.WithTimeout(ctx, rpcTimeout)
 	defer cancel()
@@ -406,7 +405,7 @@ func (s *SolanaWatcher) fetchMessageAccount(ctx context.Context, acc solana.Publ
 	if err != nil {
 		p2p.DefaultRegistry.AddErrorCount(vaa.ChainIDSolana, 1)
 		solanaConnectionErrors.WithLabelValues(string(s.commitment), "get_account_info_error").Inc()
-		s.logger.Error("failed to request account",
+		logger.Error("failed to request account",
 			zap.Error(err),
 			zap.Uint64("slot", slot),
 			zap.String("commitment", string(s.commitment)),
@@ -417,7 +416,7 @@ func (s *SolanaWatcher) fetchMessageAccount(ctx context.Context, acc solana.Publ
 	if !info.Value.Owner.Equals(s.contract) {
 		p2p.DefaultRegistry.AddErrorCount(vaa.ChainIDSolana, 1)
 		solanaConnectionErrors.WithLabelValues(string(s.commitment), "account_owner_mismatch").Inc()
-		s.logger.Error("account has invalid owner",
+		logger.Error("account has invalid owner",
 			zap.Uint64("slot", slot),
 			zap.String("commitment", string(s.commitment)),
 			zap.Stringer("account", acc),
@@ -429,27 +428,27 @@ func (s *SolanaWatcher) fetchMessageAccount(ctx context.Context, acc solana.Publ
 	if string(data[:3]) != "msg" {
 		p2p.DefaultRegistry.AddErrorCount(vaa.ChainIDSolana, 1)
 		solanaConnectionErrors.WithLabelValues(string(s.commitment), "bad_account_data").Inc()
-		s.logger.Error("account is not a message account",
+		logger.Error("account is not a message account",
 			zap.Uint64("slot", slot),
 			zap.String("commitment", string(s.commitment)),
 			zap.Stringer("account", acc))
 		return
 	}
 
-	s.logger.Info("found valid VAA account",
+	logger.Info("found valid VAA account",
 		zap.Uint64("slot", slot),
 		zap.String("commitment", string(s.commitment)),
 		zap.Stringer("account", acc),
 		zap.Binary("data", data))
 
-	s.processMessageAccount(data, acc)
+	s.processMessageAccount(logger, data, acc)
 }
 
-func (s *SolanaWatcher) processMessageAccount(data []byte, acc solana.PublicKey) {
+func (s *SolanaWatcher) processMessageAccount(logger *zap.Logger, data []byte, acc solana.PublicKey) {
 	proposal, err := ParseTransferOutProposal(data)
 	if err != nil {
 		solanaAccountSkips.WithLabelValues("parse_transfer_out").Inc()
-		s.logger.Error(
+		logger.Error(
 			"failed to parse transfer proposal",
 			zap.Stringer("account", acc),
 			zap.Binary("data", data),
@@ -473,7 +472,7 @@ func (s *SolanaWatcher) processMessageAccount(data []byte, acc solana.PublicKey)
 
 	solanaMessagesConfirmed.Inc()
 
-	s.logger.Info("message observed",
+	logger.Info("message observed",
 		zap.Stringer("account", acc),
 		zap.Time("timestamp", observation.Timestamp),
 		zap.Uint32("nonce", observation.Nonce),
```
