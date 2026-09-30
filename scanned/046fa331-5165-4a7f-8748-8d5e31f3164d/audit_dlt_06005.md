# [?] event: fix Resubscribe deadlock when unsubscribing after inner sub ends (#28359)

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2023-10-22
Source: https://github.com/etclabscore/core-geth/commit/ffc6a0f36edda396a8421cf7a3c0feb88be20d0b
Type: security-commit

## Details
event: fix Resubscribe deadlock when unsubscribing after inner sub ends (#28359)

A goroutine is used to manage the lifetime of subscriptions managed by
resubscriptions. When the subscription ends with no error, the resub
goroutine ends as well. However, the resub goroutine needs to live
long enough to read from the unsub channel. Otheriwse, an Unsubscribe
call deadlocks when writing to the unsub channel.

This is fixed by adding a buffer to the unsub channel.

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
