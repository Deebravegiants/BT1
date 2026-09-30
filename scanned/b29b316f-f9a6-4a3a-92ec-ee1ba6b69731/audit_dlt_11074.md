# [?] op-node: Fix race condition closing gossip handler.

## Summary
Severity: Unknown
Chain: Kroma
Component: kroma-network/kroma
Published: 2023-12-12
Source: https://github.com/kroma-network/kroma/commit/5769a8d2b1ac92f8ed34e64a31c1cbbc447942a3
Type: security-commit

## Details
op-node: Fix race condition closing gossip handler.

## Patch
### op-node/p2p/gossip.go
```diff
@@ -601,7 +601,6 @@ func MakeSubscriber(log log.Logger, msgHandler MessageHandler) TopicSubscriber {
 }
 
 func LogTopicEvents(ctx context.Context, log log.Logger, evHandler *pubsub.TopicEventHandler) {
-	defer evHandler.Cancel()
 	for {
 		ev, err := evHandler.NextPeerEvent(ctx)
 		if err != nil {
```
