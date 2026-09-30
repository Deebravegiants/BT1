# [?] swarm/pss: fix data race in notify_test.go (TestStart) (#18518)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-01-24
Source: https://github.com/celo-org/celo-blockchain/commit/6167dd65b572c69fde5e4583b4c3a304fc83a544
Type: security-commit

## Details
swarm/pss: fix data race in notify_test.go (TestStart) (#18518)

## Patch
### swarm/pss/notify/notify_test.go
```diff
@@ -128,7 +128,7 @@ func TestStart(t *testing.T) {
 	defer rightSub.Unsubscribe()
 
 	updateC := make(chan []byte)
-	updateMsg := []byte{}
+	var updateMsg []byte
 	ctrlClient := NewController(psses[rightPub])
 	ctrlNotifier := NewController(psses[leftPub])
 	ctrlNotifier.NewNotifier("foo.eth", 2, updateC)
@@ -145,17 +145,24 @@ func TestStart(t *testing.T) {
 	if err != nil {
 		t.Fatal(err)
 	}
+
+	copyOfUpdateMsg := make([]byte, len(updateMsg))
+	copy(copyOfUpdateMsg, updateMsg)
+	ctrlClientError := make(chan error, 1)
 	ctrlClient.Subscribe(rsrcName, pubkey, addrbytes, func(s string, b []byte) error {
-		if s != "foo.eth" || !bytes.Equal(updateMsg, b) {
-			t.Fatalf("unexpected result in client handler: '%s':'%x'", s, b)
+		if s != "foo.eth" || !bytes.Equal(copyOfUpdateMsg, b) {
+			ctrlClientError <- fmt.Errorf("unexpected result in client handler: '%s':'%x'", s, b)
+		} else {
+			log.Info("client handler receive", "s", s, "b", b)
 		}
-		log.Info("client handler receive", "s", s, "b", b)
 		return nil
 	})
 
 	var inMsg *pss.APIMsg
 	select {
 	case inMsg = <-rmsgC:
+	case err := <-ctrlClientError:
+		t.Fatal(err)
 	case <-ctx.Done():
 		t.Fatal(ctx.Err())
 	}
```
