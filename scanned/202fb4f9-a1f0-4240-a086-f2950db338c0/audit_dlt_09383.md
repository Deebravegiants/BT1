# [?] fix(engine): more consensus failure fun (#1148)

## Summary
Severity: Unknown
Chain: Berachain
Component: berachain/beacon-kit
Published: 2024-05-22
Source: https://github.com/berachain/beacon-kit/commit/0ac32e9c1094877c4e6f0c6873db4cf6ec9206e3
Type: security-commit

## Details
fix(engine): more consensus failure fun (#1148)

* bet

* bet

* bet

* bet

* bet

* bet

## Patch
### mod/execution/pkg/engine/engine.go
```diff
@@ -119,15 +119,21 @@ func (ee *Engine[
 		req.ForkVersion,
 	)
 	switch {
-	case errors.Is(err, engineerrors.ErrAcceptedPayloadStatus) ||
-		errors.Is(err, engineerrors.ErrSyncingPayloadStatus):
+	case errors.IsAny(
+		err,
+		engineerrors.ErrAcceptedPayloadStatus,
+		engineerrors.ErrSyncingPayloadStatus,
+	):
 		ee.logger.Info("forkchoice updated with optimistic block",
 			"head_eth1_hash", req.State.HeadBlockHash,
 		)
 		// telemetry.IncrCounter(1, MetricsKeyAcceptedSyncingPayloadStatus)
 		return payloadID, nil, nil
-	case errors.Is(err, engineerrors.ErrInvalidPayloadStatus) ||
-		errors.Is(err, engineerrors.ErrInvalidBlockHashPayloadStatus):
+	case errors.IsAny(
+		err,
+		engineerrors.ErrInvalidPayloadStatus,
+		engineerrors.ErrInvalidBlockHashPayloadStatus,
+	):
 		// Attempt to get the chain back into a valid state, by
 		// getting finding an ancestor block with a valid payload and
 		// forcing a recovery.
@@ -177,12 +183,16 @@ func (ee *Engine[
 			ctx,
 			req.ExecutionPayload.GetBlockHash(),
 		)
-		if header != nil && err != nil {
+
+		// If we find the header and there is no error, we can
+		// skip any payload verification, since this block must've
+		// been validated at some point in the past.
+		if header != nil && err == nil {
 			ee.logger.Info("skipping new payload, block already available",
 				"block_hash", req.ExecutionPayload.GetBlockHash(),
 			)
+			return nil
 		}
-		return nil
 	}
 
 	// Otherwise we will send the payload to the execution client.
@@ -200,8 +210,11 @@ func (ee *Engine[
 	// say that the block is valid, this is utilized during syncing
 	// to allow the beacon-chain to continue processing blocks, while
 	// its execution client is fetching things over it's p2p layer.
-	case errors.Is(err, engineerrors.ErrAcceptedPayloadStatus) ||
-		errors.Is(err, engineerrors.ErrSyncingPayloadStatus):
+	case errors.IsAny(
+		err,
+		engineerrors.ErrAcceptedPayloadStatus,
+		engineerrors.ErrSyncingPayloadStatus,
+	):
 		ee.logger.Info("new payload called with optimistic block",
 			"payload_block_hash", (req.ExecutionPayload.GetBlockHash()),
 			"parent_hash", (req.ExecutionPayload.GetParentHash()),
@@ -220,8 +233,11 @@ func (ee *Engine[
 	//
 	// These two cases are semantically the same:
 	// https://github.com/ethereum/execution-apis/issues/270
-	case errors.Is(err, engineerrors.ErrInvalidPayloadStatus) ||
-		errors.Is(err, engineerrors.ErrInvalidBlockHashPayloadStatus):
+	case errors.IsAny(
+		err,
+		engineerrors.ErrInvalidPayloadStatus,
+		engineerrors.ErrInvalidBlockHashPayloadStatus,
+	):
 		ee.logger.Error(
 			"invalid payload status",
 			"last_valid_hash", fmt.Sprintf("%#x", lastValidHash),
@@ -260,17 +276,16 @@ func (ee *Engine[
 			return nil
 		}
 		return errors.Join(err, engineerrors.ErrPreDefinedJSONRPC)
-	case errors.IsAny(err, context.Canceled, context.DeadlineExceeded):
-		if req.Optimistic {
-			ee.logger.Warn(
-				"context error during optimistic payload verification",
-				"error", err,
-			)
-			return nil
-		}
-		return err
 	}
 
-	// If we get any other error, we will just return it.
+	// If we see an error that we don't recognize we just simply forward
+	// it to the caller.
+	if req.Optimistic {
+		ee.logger.Warn(
+			"error during optimistic payload verification",
+			"error", err,
+		)
+		return nil
+	}
 	return err
 }
```
