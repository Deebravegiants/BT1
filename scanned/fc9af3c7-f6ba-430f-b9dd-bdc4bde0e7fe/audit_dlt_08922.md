# [?] node/pkg/processor: fix crash when observation is made while gs is nil

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2021-10-01
Source: https://github.com/wormhole-foundation/wormhole/commit/096707a9c4e44f2a4f883806feefef101dcf65b7
Type: security-commit

## Details
node/pkg/processor: fix crash when observation is made while gs is nil

Rare race condition. Found locally when manually injecting observations.

Change-Id: Id10d10ad4cfe38b5f4b00a30978940e928e6bc96

## Patch
### node/pkg/processor/message.go
```diff
@@ -39,6 +39,17 @@ var (
 // handleMessage processes a message received from a chain and instantiates our deterministic copy of the VAA. An
 // event may be received multiple times and must be handled in an idempotent fashion.
 func (p *Processor) handleMessage(ctx context.Context, k *common.MessagePublication) {
+	if p.gs == nil {
+		p.logger.Warn("dropping observation since we haven't initialized our guardian set yet",
+			zap.Stringer("emitter_chain", k.EmitterChain),
+			zap.Stringer("emitter_address", k.EmitterAddress),
+			zap.Uint32("nonce", k.Nonce),
+			zap.Stringer("txhash", k.TxHash),
+			zap.Time("timestamp", k.Timestamp),
+		)
+		return
+	}
+
 	supervisor.Logger(ctx).Info("message publication confirmed",
 		zap.Stringer("emitter_chain", k.EmitterChain),
 		zap.Stringer("emitter_address", k.EmitterAddress),
```
