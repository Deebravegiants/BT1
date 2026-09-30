# [?] Merge PR #1005: Fix legacy race condition

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/relayer
Published: 2022-09-23
Source: https://github.com/cosmos/relayer/commit/15840b7aa1ed169dc3c84f3e936a51b5c4db092e
Type: security-commit

## Details
Merge PR #1005: Fix legacy race condition

## Patch
### relayer/naive-strategy.go
```diff
@@ -476,31 +476,33 @@ func RelayPackets(ctx context.Context, log *zap.Logger, src, dst *Chain, sp Rela
 		return err
 	}
 
-	// set the maximum relay transaction constraints
-	msgs := &RelayMsgs{
-		Src:          []provider.RelayerMessage{},
-		Dst:          []provider.RelayerMessage{},
-		MaxTxSize:    maxTxSize,
-		MaxMsgLength: maxMsgLength,
-	}
-
 	eg, egCtx := errgroup.WithContext(ctx)
 	// add messages for sequences on src
+	var msgsSrc1, msgsDst1 []provider.RelayerMessage
 	eg.Go(func() error {
-		return AddMessagesForSequences(egCtx, sp.Src, src, dst, srch, dsth, &msgs.Src, &msgs.Dst,
+		return AddMessagesForSequences(egCtx, sp.Src, src, dst, srch, dsth, &msgsSrc1, &msgsDst1,
 			srcChannel.ChannelId, srcChannel.PortId, srcChannel.Counterparty.ChannelId, srcChannel.Counterparty.PortId, srcChannel.Ordering)
 	})
 
+	var msgsSrc2, msgsDst2 []provider.RelayerMessage
 	// add messages for sequences on dst
 	eg.Go(func() error {
-		return AddMessagesForSequences(egCtx, sp.Dst, dst, src, dsth, srch, &msgs.Dst, &msgs.Src,
+		return AddMessagesForSequences(egCtx, sp.Dst, dst, src, dsth, srch, &msgsDst2, &msgsSrc2,
 			srcChannel.Counterparty.ChannelId, srcChannel.Counterparty.PortId, srcChannel.ChannelId, srcChannel.PortId, srcChannel.Ordering)
 	})
 
 	if err = eg.Wait(); err != nil {
 		return err
 	}
 
+	// set the maximum relay transaction constraints
+	msgs := &RelayMsgs{
+		Src:          append(msgsSrc1, msgsSrc2...),
+		Dst:          append(msgsDst1, msgsDst2...),
+		MaxTxSize:    maxTxSize,
+		MaxMsgLength: maxMsgLength,
+	}
+
 	if !msgs.Ready() {
 		log.Info(
 			"No packets to relay",
```
