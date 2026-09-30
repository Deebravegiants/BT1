# [?] discovery: fix gossiper shutdown deadlock

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2026-02-02
Source: https://github.com/lightningnetwork/lnd/commit/21588acb3d5b9b4bb605b0852c91f10b6bb2a1c6
Type: security-commit

## Details
discovery: fix gossiper shutdown deadlock

When processing a remote network announcement, it is possible for two
error messages to be sent back on the errChan.  Since Brontide doesn't
actually read from errChan, and since errChan only buffered one error
message, the sending goroutine would deadlock forever.  This would only
become apparent when the gossiper attempted to shut down and got hung
up.

For now, we can fix this simply by buffering up to two error messages on
errChan.  There is an existing TODO to restructure this logic entirely
to use the actor model, and we can do a more thorough fix as part of
that work.

This bug was discovered while doing full node fuzz testing and was
triggered by sending a specific channel_announcement message and then
shutting down LND.

## Patch
### discovery/gossiper.go
```diff
@@ -880,7 +880,14 @@ func (d *AuthenticatedGossiper) stop() {
 func (d *AuthenticatedGossiper) ProcessRemoteAnnouncement(ctx context.Context,
 	msg lnwire.Message, peer lnpeer.Peer) chan error {
 
-	errChan := make(chan error, 1)
+	// Buffer up to two messages on errChan since up to two messages may be
+	// written and not all callers of this function actually read from
+	// errChan. Without this buffer goroutines end up blocking on writes to
+	// errChan, which prevents the gossiper from shutting down cleanly.
+	//
+	// TODO(ziggie): Redesign this once the actor model pattern becomes
+	// available. See https://github.com/lightningnetwork/lnd/pull/9820.
+	errChan := make(chan error, 2)
 
 	// For messages in the known set of channel series queries, we'll
 	// dispatch the message directly to the GossipSyncer, and skip the main
```

### discovery/gossiper_test.go
```diff
@@ -5236,3 +5236,64 @@ func TestRecoverGossipPanicNilJobID(t *testing.T) {
 		t.Fatal("timeout waiting for error")
 	}
 }
+
+// TestGossiperShutdownWrongChainAnnouncement tests that the gossiper can shut
+// down cleanly after processing a channel announcement with the wrong chain
+// hash. This is a regression test for a bug where the gossiper would deadlock
+// on shutdown because more errors were sent on the error channel than it would
+// buffer, and no one was reading those error messages.
+//
+// In this test we trigger the sending of two error messages:
+// 1. First send when rejecting the wrong-chain announcement
+// 2. Second send when SignalDependents returns an error
+//
+// Since the error channel had a buffer of 1, the second send would block
+// forever, preventing the goroutine from completing and causing Stop() to hang
+// on wg.Wait().
+func TestGossiperShutdownWrongChainAnnouncement(t *testing.T) {
+	t.Parallel()
+
+	// Create a test context with the gossiper configured for MainNet.
+	tCtx, err := createTestCtx(t, 0, false)
+	require.NoError(t, err)
+
+	// Create a channel announcement with:
+	// 1. Wrong chain hash (SimNet instead of MainNet)
+	// 2. NodeID1 == NodeID2
+	//
+	// The first condition triggers the first error message to be sent, and
+	// the second condition causes SignalDependents to attempt to remove the
+	// same dependent job twice, which then triggers the second error
+	// message to be sent.
+	wrongChainAnn := &lnwire.ChannelAnnouncement1{
+		ChainHash: *chaincfg.SimNetParams.GenesisHash,
+		ShortChannelID: lnwire.ShortChannelID{
+			BlockHeight: 1,
+			TxIndex:     0,
+			TxPosition:  0,
+		},
+		Features: testFeatures,
+	}
+	// Use the SAME public key for NodeID1 and NodeID2 to trigger the
+	// second error message.
+	copy(wrongChainAnn.NodeID1[:], remoteKeyPub1.SerializeCompressed())
+	copy(wrongChainAnn.NodeID2[:], remoteKeyPub1.SerializeCompressed())
+	copy(wrongChainAnn.BitcoinKey1[:], bitcoinKeyPub1.SerializeCompressed())
+	copy(wrongChainAnn.BitcoinKey2[:], bitcoinKeyPub2.SerializeCompressed())
+
+	nodePeer := &mockPeer{remoteKeyPub1, nil, nil, atomic.Bool{}}
+
+	// Process the announcement without reading from the error channel,
+	// exactly as Brontide does.
+	_ = tCtx.gossiper.ProcessRemoteAnnouncement(
+		t.Context(), wrongChainAnn, nodePeer,
+	)
+
+	// Give the gossiper time to process the announcement.
+	time.Sleep(100 * time.Millisecond)
+
+	// Now stop the gossiper. This should complete without hanging.
+	// If the bug is present, Stop() will hang forever because a goroutine
+	// is blocked trying to send to the error channel a second time.
+	require.NoError(t, tCtx.gossiper.Stop())
+}
```
