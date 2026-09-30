# [?] p2p/pex: fix DATA RACE

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2020-04-20
Source: https://github.com/cometbft/cometbft/commit/ec1c657d5ab87086790760173dbd45b619faa3ee
Type: security-commit

## Details
p2p/pex: fix DATA RACE

in TestPEXReactorDialsPeerUpToMaxAttemptsInSeedMode

Closes #4668

______

For contributor use:

- [x] Wrote tests
- [ ] ~~Updated CHANGELOG_PENDING.md~~
- [x] Linked to Github issue with discussion and accepted design OR link to spec that describes this work.
- [ ] ~~Updated relevant documentation (`docs/`) and code comments~~
- [x] Re-reviewed `Files changed` in the Github PR explorer

## Patch
### p2p/pex/pex_reactor_test.go
```diff
@@ -378,9 +378,7 @@ func TestPEXReactorDialsPeerUpToMaxAttemptsInSeedMode(t *testing.T) {
 
 	sw := createSwitchAndAddReactors(pexR)
 	sw.SetAddrBook(book)
-	err = sw.Start()
-	require.NoError(t, err)
-	defer sw.Stop()
+	// No need to start sw since crawlPeers is called manually here.
 
 	peer := mock.NewPeer(nil)
 	addr := peer.SocketAddr()
@@ -389,9 +387,11 @@ func TestPEXReactorDialsPeerUpToMaxAttemptsInSeedMode(t *testing.T) {
 	require.NoError(t, err)
 
 	assert.True(t, book.HasAddress(addr))
+
 	// imitate maxAttemptsToDial reached
 	pexR.attemptsToDial.Store(addr.DialString(), _attemptsToDial{maxAttemptsToDial + 1, time.Now()})
 	pexR.crawlPeers([]*p2p.NetAddress{addr})
+
 	assert.False(t, book.HasAddress(addr))
 }
 
```
