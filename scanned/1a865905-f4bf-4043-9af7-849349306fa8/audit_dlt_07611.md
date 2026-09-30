# [?] les: fix panic in ultralight client sync (#24641)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2022-04-08
Source: https://github.com/ethereum/go-ethereum/commit/c1b69bd12184cc6278f5641c14bc72ca0a42d397
Type: security-commit

## Details
les: fix panic in ultralight client sync (#24641)

## Patch
### les/fetcher.go
```diff
@@ -441,6 +441,14 @@ func (f *lightFetcher) mainloop() {
 			if ulc {
 				head := f.chain.CurrentHeader()
 				ancestor := rawdb.FindCommonAncestor(f.chaindb, origin, head)
+
+				// Recap the ancestor with genesis header in case the ancestor
+				// is not found. It can happen the original head is before the
+				// checkpoint while the synced headers are after it. In this
+				// case there is no ancestor between them.
+				if ancestor == nil {
+					ancestor = f.chain.Genesis().Header()
+				}
 				var untrusted []common.Hash
 				for head.Number.Cmp(ancestor.Number) > 0 {
 					hash, number := head.Hash(), head.Number.Uint64()
@@ -449,6 +457,9 @@ func (f *lightFetcher) mainloop() {
 					}
 					untrusted = append(untrusted, hash)
 					head = f.chain.GetHeader(head.ParentHash, number-1)
+					if head == nil {
+						break // all the synced headers will be dropped
+					}
 				}
 				if len(untrusted) > 0 {
 					for i, j := 0, len(untrusted)-1; i < j; i, j = i+1, j-1 {
@@ -514,7 +525,7 @@ func (f *lightFetcher) requestHeaderByHash(peerid enode.ID) func(common.Hash) er
 	}
 }
 
-// requestResync invokes synchronisation callback to start syncing.
+// startSync invokes synchronisation callback to start syncing.
 func (f *lightFetcher) startSync(id enode.ID) {
 	defer func(header *types.Header) {
 		f.syncDone <- header
```

### les/fetcher_test.go
```diff
@@ -25,6 +25,7 @@ import (
 	"github.com/ethereum/go-ethereum/core"
 	"github.com/ethereum/go-ethereum/core/rawdb"
 	"github.com/ethereum/go-ethereum/core/types"
+	"github.com/ethereum/go-ethereum/light"
 	"github.com/ethereum/go-ethereum/p2p/enode"
 	"github.com/ethereum/go-ethereum/params"
 )
@@ -152,23 +153,36 @@ func TestTrustedAnnouncementsLes2(t *testing.T) { testTrustedAnnouncement(t, 2)
 func TestTrustedAnnouncementsLes3(t *testing.T) { testTrustedAnnouncement(t, 3) }
 
 func testTrustedAnnouncement(t *testing.T, protocol int) {
+	//log.Root().SetHandler(log.LvlFilterHandler(log.LvlDebug, log.StreamHandler(os.Stderr, log.TerminalFormat(true))))
 	var (
 		servers   []*testServer
 		teardowns []func()
 		nodes     []*enode.Node
 		ids       []string
 		cpeers    []*clientPeer
 		speers    []*serverPeer
+
+		config       = light.TestServerIndexerConfig
+		waitIndexers = func(cIndexer, bIndexer, btIndexer *core.ChainIndexer) {
+			for {
+				cs, _, _ := cIndexer.Sections()
+				bts, _, _ := btIndexer.Sections()
+				if cs >= 2 && bts >= 2 {
+					break
+				}
+				time.Sleep(10 * time.Millisecond)
+			}
+		}
 	)
-	for i := 0; i < 10; i++ {
-		s, n, teardown := newTestServerPeer(t, 10, protocol)
+	for i := 0; i < 4; i++ {
+		s, n, teardown := newTestServerPeer(t, int(2*config.ChtSize+config.ChtConfirms), protocol, waitIndexers)
 
 		servers = append(servers, s)
 		nodes = append(nodes, n)
 		teardowns = append(teardowns, teardown)
 
 		// A half of them are trusted servers.
-		if i < 5 {
+		if i < 2 {
 			ids = append(ids, n.String())
 		}
 	}
@@ -185,6 +199,18 @@ func testTrustedAnnouncement(t *testing.T, protocol int) {
 			teardowns[i]()
 		}
 	}()
+
+	// Register the assembled checkpoint as hardcoded one.
+	head := servers[0].chtIndexer.SectionHead(0)
+	cp := &params.TrustedCheckpoint{
+		SectionIndex: 0,
+		SectionHead:  head,
+		CHTRoot:      light.GetChtRoot(servers[0].db, 0, head),
+		BloomRoot:    light.GetBloomTrieRoot(servers[0].db, 0, head),
+	}
+	c.handler.checkpoint = cp
+	c.handler.backend.blockchain.AddTrustedCheckpoint(cp)
+
 	// Connect all server instances.
 	for i := 0; i < len(servers); i++ {
 		sp, cp, err := connect(servers[i].handler, nodes[i].ID(), c.handler, protocol, true)
@@ -218,9 +244,9 @@ func testTrustedAnnouncement(t *testing.T, protocol int) {
 		}
 		verifyChainHeight(t, c.handler.fetcher, expected)
 	}
-	check([]uint64{1}, 1, func() { <-newHead })   // Sequential announcements
-	check([]uint64{4}, 4, func() { <-newHead })   // ULC-style light syncing, rollback untrusted headers
-	check([]uint64{10}, 10, func() { <-newHead }) // Sync the whole chain.
+	check([]uint64{1}, 1, func() { <-newHead })                                                                       // Sequential announcements
+	check([]uint64{config.ChtSize + config.ChtConfirms}, config.ChtSize+config.ChtConfirms, func() { <-newHead })     // ULC-style light syncing, rollback untrusted headers
+	check([]uint64{2*config.ChtSize + config.ChtConfirms}, 2*config.ChtSize+config.ChtConfirms, func() { <-newHead }) // Sync the whole chain.
 }
 
 func TestInvalidAnnouncesLES2(t *testing.T) { testInvalidAnnounces(t, lpv2) }
```

### les/ulc_test.go
```diff
@@ -55,7 +55,7 @@ func testULCAnnounceThreshold(t *testing.T, protocol int) {
 			ids       []string
 		)
 		for i := 0; i < len(testcase.height); i++ {
-			s, n, teardown := newTestServerPeer(t, 0, protocol)
+			s, n, teardown := newTestServerPeer(t, 0, protocol, nil)
 
 			servers = append(servers, s)
 			nodes = append(nodes, n)
@@ -132,10 +132,11 @@ func connect(server *serverHandler, serverId enode.ID, client *clientHandler, pr
 }
 
 // newTestServerPeer creates server peer.
-func newTestServerPeer(t *testing.T, blocks int, protocol int) (*testServer, *enode.Node, func()) {
+func newTestServerPeer(t *testing.T, blocks int, protocol int, indexFn indexerCallback) (*testServer, *enode.Node, func()) {
 	netconfig := testnetConfig{
 		blocks:    blocks,
 		protocol:  protocol,
+		indexFn:   indexFn,
 		nopruning: true,
 	}
 	s, _, teardown := newClientServerEnv(t, netconfig)
```
