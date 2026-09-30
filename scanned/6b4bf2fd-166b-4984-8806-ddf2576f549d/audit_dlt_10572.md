# [?] Merge pull request #943 from libp2p/fix/record-panic

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2020-05-20
Source: https://github.com/libp2p/go-libp2p/commit/937067939bcd43be8f768cdecadf301656e5cbb7
Type: security-commit

## Details
Merge pull request #943 from libp2p/fix/record-panic

fix: don't try to marshal a nil record

## Patch
### p2p/protocol/identify/id.go
```diff
@@ -428,9 +428,6 @@ func (ids *IDService) getSnapshot() *identifySnapshot {
 	if !ids.disableSignedPeerRecord {
 		if cab, ok := peerstore.GetCertifiedAddrBook(ids.Host.Peerstore()); ok {
 			snapshot.record = cab.GetPeerRecord(ids.Host.ID())
-			if snapshot.record == nil {
-				log.Errorf("latest peer record does not exist. identify message incomplete!")
-			}
 		}
 	}
 	snapshot.addrs = ids.Host.Addrs()
@@ -465,7 +462,7 @@ func (ids *IDService) populateMessage(
 		mes.ListenAddrs = append(mes.ListenAddrs, addr.Bytes())
 	}
 
-	if !ids.disableSignedPeerRecord {
+	if !ids.disableSignedPeerRecord && snapshot.record != nil {
 		recBytes, err := snapshot.record.Marshal()
 		if err != nil {
 			log.Errorf("error marshaling peer record: %v", err)
```

### p2p/protocol/identify/id_test.go
```diff
@@ -686,6 +686,37 @@ func TestUserAgent(t *testing.T) {
 	}
 }
 
+func TestNotListening(t *testing.T) {
+	// Make sure we don't panic if we're not listening on any addresses.
+	//
+	// https://github.com/libp2p/go-libp2p/issues/939
+	ctx, cancel := context.WithCancel(context.Background())
+	defer cancel()
+
+	h1, err := libp2p.New(
+		ctx,
+		libp2p.NoListenAddrs,
+	)
+	if err != nil {
+		t.Fatal(err)
+	}
+	defer h1.Close()
+
+	h2, err := libp2p.New(
+		ctx,
+		libp2p.ListenAddrStrings("/ip4/127.0.0.1/tcp/0"),
+	)
+	if err != nil {
+		t.Fatal(err)
+	}
+	defer h2.Close()
+
+	err = h1.Connect(ctx, peer.AddrInfo{ID: h2.ID(), Addrs: h2.Addrs()})
+	if err != nil {
+		t.Fatal(err)
+	}
+}
+
 func TestSendPushIfDeltaNotSupported(t *testing.T) {
 	ctx, cancel := context.WithCancel(context.Background())
 	defer cancel()
```
