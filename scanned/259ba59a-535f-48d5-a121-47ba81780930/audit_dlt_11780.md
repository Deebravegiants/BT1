# [?] Fix potential panic when subscribing to topic fails (#830)

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/go-f3
Published: 2025-01-16
Source: https://github.com/filecoin-project/go-f3/commit/935bafa5a381ed22ef73a5e8cbe8d601698e99b8
Type: security-commit

## Details
Fix potential panic when subscribing to topic fails (#830)

Avoid referencing subscription when constructing an error message as it
may be nil when subscription fails.

## Patch
### host.go
```diff
@@ -640,7 +640,7 @@ func (h *gpbftRunner) startPubsub() (<-chan gpbft.ValidatedMessage, error) {
 	)
 	sub, err := h.topic.Subscribe(pubsub.WithBufferSize(subBufferSize))
 	if err != nil {
-		return nil, fmt.Errorf("could not subscribe to pubsub topic: %s: %w", sub.Topic(), err)
+		return nil, fmt.Errorf("could not subscribe to pubsub topic: %s: %w", h.topic, err)
 	}
 
 	messageQueue := make(chan gpbft.ValidatedMessage, msgQueueBufferSize)
```
