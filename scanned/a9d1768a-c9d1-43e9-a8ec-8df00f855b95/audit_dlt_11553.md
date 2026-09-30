# [?] Prevent uint256 overflow during conversion (#45)

## Summary
Severity: Unknown
Chain: MEV
Component: flashbots/builder
Published: 2023-03-13
Source: https://github.com/flashbots/builder/commit/211bb0949fa178ff37d7779d7bb225e902edc0a9
Type: security-commit

## Details
Prevent uint256 overflow during conversion (#45)

* Prevent uint256 overflow during conversion

* add shanghai checks

* remove unused functions

* move validation to ValidatePayload

## Patch
### builder/builder.go
```diff
@@ -166,18 +166,18 @@ func (b *Builder) submitBellatrixBlock(block *types.Block, blockValue *big.Int,
 	if b.dryRun {
 		err = b.validator.ValidateBuilderSubmissionV1(&blockvalidation.BuilderBlockValidationRequest{BuilderSubmitBlockRequest: blockSubmitReq, RegisteredGasLimit: vd.GasLimit})
 		if err != nil {
-			log.Error("could not validate block", "err", err)
+			log.Error("could not validate bellatrix block", "err", err)
 		}
 	} else {
 		go b.ds.ConsumeBuiltBlock(block, blockValue, ordersClosedAt, sealedAt, commitedBundles, allBundles, &blockBidMsg)
 		err = b.relay.SubmitBlock(&blockSubmitReq, vd)
 		if err != nil {
-			log.Error("could not submit block", "err", err, "#commitedBundles", len(commitedBundles))
+			log.Error("could not submit bellatrix block", "err", err, "#commitedBundles", len(commitedBundles))
 			return err
 		}
 	}
 
-	log.Info("submitted block", "slot", blockBidMsg.Slot, "value", blockBidMsg.Value.String(), "parent", blockBidMsg.ParentHash, "hash", block.Hash(), "#commitedBundles", len(commitedBundles))
+	log.Info("submitted bellatrix block", "slot", blockBidMsg.Slot, "value", blockBidMsg.Value.String(), "parent", blockBidMsg.ParentHash, "hash", block.Hash(), "#commitedBundles", len(commitedBundles))
 
 	return nil
 }
@@ -190,10 +190,9 @@ func (b *Builder) submitCapellaBlock(block *types.Block, blockValue *big.Int, or
 		return err
 	}
 
-	value := new(boostTypes.U256Str)
-	err = value.FromBig(blockValue)
-	if err != nil {
-		log.Error("could not set block value", "err", err)
+	value, overflow := uint256.FromBig(blockValue)
+	if overflow {
+		log.Error("could not set block value due to value overflow")
 		return err
 	}
 
@@ -206,10 +205,14 @@ func (b *Builder) submitCapellaBlock(block *types.Block, blockValue *big.Int, or
 		ProposerFeeRecipient: bellatrix.ExecutionAddress(vd.FeeRecipient),
 		GasLimit:             executableData.ExecutionPayload.GasLimit,
 		GasUsed:              executableData.ExecutionPayload.GasUsed,
-		Value:                uint256.NewInt(value.BigInt().Uint64()),
+		Value:                value,
 	}
 
-	boostBidTrace := convertBidTrace(blockBidMsg)
+	boostBidTrace, err := convertBidTrace(blockBidMsg)
+	if err != nil {
+		log.Error("could not convert bid trace", "err", err)
+		return err
+	}
 
 	signature, err := boostTypes.SignMessage(&blockBidMsg, b.builderSigningDomain, b.builderSecretKey)
 	if err != nil {
@@ -223,12 +226,21 @@ func (b *Builder) submitCapellaBlock(block *types.Block, blockValue *big.Int, or
 		ExecutionPayload: payload,
 	}
 
-	go b.ds.ConsumeBuiltBlock(block, blockValue, ordersClosedAt, sealedAt, commitedBundles, allBundles, &boostBidTrace)
-	err = b.relay.SubmitBlockCapella(&blockSubmitReq, vd)
-	if err != nil {
-		log.Error("could not submit block", "err", err, "#commitedBundles", len(commitedBundles))
-		return err
+	if b.dryRun {
+		err = b.validator.ValidateBuilderSubmissionV2(&blockvalidation.BuilderBlockValidationRequestV2{SubmitBlockRequest: blockSubmitReq, RegisteredGasLimit: vd.GasLimit})
+		if err != nil {
+			log.Error("could not validate block for capella", "err", err)
+		}
+	} else {
+		go b.ds.ConsumeBuiltBlock(block, blockValue, ordersClosedAt, sealedAt, commitedBundles, allBundles, &boostBidTrace)
+		err = b.relay.SubmitBlockCapella(&blockSubmitReq, vd)
+		if err != nil {
+			log.Error("could not submit capella block", "err", err, "#commitedBundles", len(commitedBundles))
+			return err
+		}
 	}
+
+	log.Info("submitted capella block", "slot", blockBidMsg.Slot, "value", blockBidMsg.Value.String(), "parent", blockBidMsg.ParentHash, "hash", block.Hash(), "#commitedBundles", len(commitedBundles))
 	return nil
 }
 
@@ -444,7 +456,13 @@ func executableDataToCapellaExecutionPayload(data *engine.ExecutableData) (*cape
 	}, nil
 }
 
-func convertBidTrace(bidTrace apiv1.BidTrace) boostTypes.BidTrace {
+func convertBidTrace(bidTrace apiv1.BidTrace) (boostTypes.BidTrace, error) {
+	value := new(boostTypes.U256Str)
+	err := value.FromBig(bidTrace.Value.ToBig())
+	if err != nil {
+		return boostTypes.BidTrace{}, err
+	}
+
 	return boostTypes.BidTrace{
 		Slot:                 bidTrace.Slot,
 		ParentHash:           boostTypes.Hash(bidTrace.ParentHash),
@@ -454,6 +472,6 @@ func convertBidTrace(bidTrace apiv1.BidTrace) boostTypes.BidTrace {
 		ProposerFeeRecipient: boostTypes.Address(bidTrace.ProposerFeeRecipient),
 		GasLimit:             bidTrace.GasLimit,
 		GasUsed:              bidTrace.GasUsed,
-		Value:                boostTypes.IntToU256(bidTrace.Value.Uint64()),
-	}
+		Value:                *value,
+	}, nil
 }
```

### core/block_validator.go
```diff
@@ -81,7 +81,7 @@ func (v *BlockValidator) ValidateBody(block *types.Block) error {
 		// Withdrawals are not allowed prior to shanghai fork
 		return fmt.Errorf("withdrawals present in block body")
 	}
-
+	
 	if !v.bc.HasBlockAndState(block.ParentHash(), block.NumberU64()-1) {
 		if !v.bc.HasBlock(block.ParentHash(), block.NumberU64()-1) {
 			return consensus.ErrUnknownAncestor
```

### core/blockchain.go
```diff
@@ -2532,6 +2532,20 @@ func (bc *BlockChain) ValidatePayload(block *types.Block, feeRecipient common.Ad
 		return err
 	}
 
+	if bc.Config().IsShanghai(header.Time) {
+		if header.WithdrawalsHash == nil {
+			return fmt.Errorf("withdrawals hash is missing")
+		}
+		// withdrawals hash and withdrawals validated later in ValidateBody
+	} else {
+		if header.WithdrawalsHash != nil {
+			return fmt.Errorf("withdrawals hash present before shanghai")
+		}
+		if block.Withdrawals() != nil {
+			return fmt.Errorf("withdrawals list present in block body before shanghai")
+		}
+	}
+
 	if err := bc.validator.ValidateBody(block); err != nil {
 		return err
 	}
```

### eth/block-validation/api.go
```diff
@@ -18,7 +18,6 @@ import (
 	"github.com/ethereum/go-ethereum/log"
 	"github.com/ethereum/go-ethereum/node"
 	"github.com/ethereum/go-ethereum/rpc"
-	"github.com/ethereum/go-ethereum/trie"
 
 	boostTypes "github.com/flashbots/go-boost-utils/types"
 )
@@ -67,22 +66,6 @@ func (a *AccessVerifier) verifyTransactions(signer types.Signer, txs types.Trans
 	return nil
 }
 
-func verifyWithdrawals(withdrawals types.Withdrawals, expectedWithdrawalsRoot common.Hash, isShanghai bool) error {
-	if !isShanghai {
-		// Reject payload attributes with withdrawals before shanghai
-		if withdrawals != nil {
-			return errors.New("withdrawals before shanghai")
-		}
-		return nil
-	}
-
-	withdrawalsRoot := types.DeriveSha(types.Withdrawals(withdrawals), trie.NewStackTrie(nil))
-	if withdrawalsRoot != expectedWithdrawalsRoot {
-		return fmt.Errorf("withdrawals mismatch")
-	}
-	return nil
-}
-
 func NewAccessVerifierFromFile(path string) (*AccessVerifier, error) {
 	bytes, err := os.ReadFile(path)
 	if err != nil {
```
