# [?] event: fix Resubscribe deadlock when unsubscribing after inner sub ends

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/op-geth
Published: 2023-11-12
Source: https://github.com/ethereum-optimism/op-geth/commit/48c27a617b83de559f7b21f4746ee3402983a6da
Type: security-commit

## Details
event: fix Resubscribe deadlock when unsubscribing after inner sub ends

Cherry-pick changes from https://github.com/ethereum/go-ethereum/pull/28359/

## Patch
### event/subscription.go
```diff
@@ -120,7 +120,7 @@ func ResubscribeErr(backoffMax time.Duration, fn ResubscribeErrFunc) Subscriptio
 		backoffMax: backoffMax,
 		fn:         fn,
 		err:        make(chan error),
-		unsub:      make(chan struct{}),
+		unsub:      make(chan struct{}, 1),
 	}
 	go s.loop()
 	return s
```

### event/subscription_test.go
```diff
@@ -154,3 +154,27 @@ func TestResubscribeWithErrorHandler(t *testing.T) {
 		t.Fatalf("unexpected subscription errors %v, want %v", subErrs, expectedSubErrs)
 	}
 }
+
+func TestResubscribeWithCompletedSubscription(t *testing.T) {
+	t.Parallel()
+
+	quitProducerAck := make(chan struct{})
+	quitProducer := make(chan struct{})
+
+	sub := ResubscribeErr(100*time.Millisecond, func(ctx context.Context, lastErr error) (Subscription, error) {
+		return NewSubscription(func(unsubscribed <-chan struct{}) error {
+			select {
+			case <-quitProducer:
+				quitProducerAck <- struct{}{}
+				return nil
+			case <-unsubscribed:
+				return nil
+			}
+		}), nil
+	})
+
+	// Ensure producer has started and exited before Unsubscribe
+	close(quitProducer)
+	<-quitProducerAck
+	sub.Unsubscribe()
+}
```
