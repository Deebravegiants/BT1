# [?] blockchain: Fix race condition in notifications_test

## Summary
Severity: Unknown
Chain: Bitcoin
Component: btcsuite/btcd
Published: 2017-08-15
Source: https://github.com/btcsuite/btcd/commit/ca9baf77ec548f65f2fee6070251dbefa37abdf3
Type: security-commit

## Details
blockchain: Fix race condition in notifications_test

## Patch
### blockchain/notifications_test.go
```diff
@@ -6,7 +6,6 @@ package blockchain_test
 
 import (
 	"testing"
-	"time"
 
 	"github.com/btcsuite/btcd/blockchain"
 	"github.com/btcsuite/btcd/chaincfg"
@@ -27,24 +26,26 @@ func TestNotifications(t *testing.T) {
 	}
 	defer teardownFunc()
 
-	notifications := make(chan blockchain.Notification)
-	chain.Subscribe(func(notification *blockchain.Notification) {
-		go func() {
-			notifications <- *notification
-		}()
-	})
+	notificationCount := 0
+
+	callback := func(notification *blockchain.Notification) {
+		if notification.Type == blockchain.NTBlockAccepted {
+			notificationCount++
+		}
+	}
+
+	// Register callback 3 times then assert it is called three times
+	chain.Subscribe(callback)
+	chain.Subscribe(callback)
+	chain.Subscribe(callback)
 
 	_, _, err = chain.ProcessBlock(blocks[1], blockchain.BFNone)
 	if err != nil {
 		t.Fatalf("ProcessBlock fail on block 1: %v\n", err)
 	}
 
-	select {
-	case notification := <-notifications:
-		if notification.Type != blockchain.NTBlockAccepted {
-			t.Errorf("Expected NTBlockAccepted notification, got %v", notification.Type)
-		}
-	case <-time.After(time.Second):
-		t.Error("Expected blockchain notification callback to fire")
+	if notificationCount != 3 {
+		t.Fatalf("Expected notification callback to be executed 3 times, found %d",
+			notificationCount)
 	}
 }
```
