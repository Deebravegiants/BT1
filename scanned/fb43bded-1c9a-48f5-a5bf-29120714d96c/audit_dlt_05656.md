# [?] Fix/addtrustedpeer empty addrs panic (#16757)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-06-29
Source: https://github.com/OffchainLabs/prysm/commit/1d4007b60cb56becd64360ccdd28e616face7971
Type: security-commit

## Details
Fix/addtrustedpeer empty addrs panic (#16757)

**What type of PR is this?**

Bug fix


**What does this PR do? Why is it needed?**

`AddTrustedPeer` parses a peer multiaddr and then indexes
`info.Addrs[0]` without checking whether any transport address was
present. A peer-only multiaddr such as `/p2p/<peer_id>` can parse
successfully while producing an `AddrInfo` with an empty `Addrs` slice.
The unchecked index then panics. The same pattern also exists in
`connectWithAllTrustedPeers`.

This PR fixes this by:
- Added a length check after parsing the address in `AddTrustedPeer`.
- Skipped peers that have no dialable address before indexing `Addrs[0]`
in `connectWithAllTrustedPeers` and `peerIdsFromMultiAddrs`.
- Added `TestAddTrustedPeer_NoTransportAddress` to verify the handler
returns `400 Bad Request` instead of panicking.

**Which issue(s) does this PR fix?**

None.

**Other notes for review**

The test results before the fix:
```
$ go test ./beacon-chain/rpc/prysm/node -run '^TestAddTrustedPeer_NoTransportAddress$' -count=1
--- FAIL: TestAddTrustedPeer_NoTransportAddress (0.00s)
panic: runtime error: index out of range [0] with length 0 [recovered, repanicked]

goroutine 307 [running]:
testing.tRunner.func1.2({0x1a3d860, 0xc0000547e0})
        /home/alleysira/go/pkg/mod/golang.org/toolchain@v0.0.1-go1.25.1.linux-amd64/src/testing/testing.go:1872 +0x237
testing.tRunner.func1()
        /home/alleysira/go/pkg/mod/golang.org/toolchain@v0.0.1-go1.25.1.linux-amd64/src/testing/testing.go:1875 +0x35b
panic({0x1a3d860?, 0xc0000547e0?})
        /home/alleysira/go/pkg/mod/golang.org/toolchain@v0.0.1-go1.25.1.linux-amd64/src/runtime/panic.go:783 +0x132
github.com/OffchainLabs/prysm/v7/beacon-chain/rpc/prysm/node.(*Server).AddTrustedPeer(0xc0004d9e98, {0x1f5ee28, 0xc0005161c0}, 0xc0003bef00)
        /home/alleysira/pr/prysm/beacon-chain/rpc/prysm/node/handlers.go:98 +0x4db
github.com/OffchainLabs/prysm/v7/beacon-chain/rpc/prysm/node.TestAddTrustedPeer_NoTransportAddress(0xc000102fc0)
        /home/alleysira/pr/prysm/beacon-chain/rpc/prysm/node/handlers_test.go:233 +0x1e6
testing.tRunner(0xc000102fc0, 0x1d6d238)
        /home/alleysira/go/pkg/mod/golang.org/toolchain@v0.0.1-go1.25.1.linux-amd64/src/testing/testing.go:1934 +0xea
created by testing.(*T).Run in goroutine 1
        /home/alleysira/go/pkg/mod/golang.org/toolchain@v0.0.1-go1.25.1.linux-amd64/src/testing/testing.go:1997 +0x465
FAIL    github.com/OffchainLabs/prysm/v7/beacon-chain/rpc/prysm/node    0.026s
FAIL
```

With this fix:
```
$ go test ./beacon-chain/rpc/prysm/node -run '^TestAddTrustedPeer_NoTransportAddress$' -count=1
ok      github.com/OffchainLabs/prysm/v7/beacon-chain/rpc/prysm/node    0.026s
```

Other existing tests:
```
$ go test ./beacon-chain/rpc/prysm/node ./beacon-chain/p2p -count=1
ok      github.com/OffchainLabs/prysm/v7/beacon-chain/rpc/prysm/node    0.025s
ok      github.com/OffchainLabs/prysm/v7/beacon-chain/p2p       38.553s
```

**Acknowledgements**

- [x] I have read
[CONTRIBUTING.md](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md).
- [x] I have included a uniquely named [changelog fragment
file](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md#maintaining-changelogmd).
- [x] I have added a description with sufficient context for reviewers
to understand this PR.
- [x] I have tested that my changes work as expected and I added a
testing plan to the PR description (if applicable).

Thanks for your attention!

### beacon-chain/p2p/discovery.go
```diff
@@ -1001,6 +1001,10 @@ func peerIdsFromMultiAddrs(addrs []ma.Multiaddr) []peer.ID {
 			log.WithError(err).Errorf("Could not derive peer info from multiaddress %s", a.String())
 			continue
 		}
+		if len(info.Addrs) == 0 {
+			log.WithField("peerID", info.ID).Warn("Skipping peer with no transport address")
+			continue
+		}
 		peers = append(peers, info.ID)
 	}
 	return peers
```

### beacon-chain/p2p/service.go
```diff
@@ -488,6 +488,10 @@ func (s *Service) connectWithAllTrustedPeers(multiAddrs []multiaddr.Multiaddr) {
 		return
 	}
 	for _, info := range addrInfos {
+		if len(info.Addrs) == 0 {
+			log.WithField("peerID", info.ID).Warn("Skipping trusted peer with no transport address")
+			continue
+		}
 		// add peer into peer status
 		s.peers.Add(nil, info.ID, info.Addrs[0], network.DirUnknown)
 		// make each dial non-blocking
```

### beacon-chain/rpc/prysm/node/handlers.go
```diff
@@ -84,7 +84,14 @@ func (s *Server) AddTrustedPeer(w http.ResponseWriter, r *http.Request) {
 		httputil.WriteError(w, errJson)
 		return
 	}
-
+	if len(info.Addrs) == 0 {
+		errJson := &httputil.DefaultJsonError{
+			Message: "Multiaddress must include a transport address",
+			Code:    http.StatusBadRequest,
+		}
+		httputil.WriteError(w, errJson)
+		return
+	}
 	// also add new peerdata to peers
 	direction, err := s.PeersFetcher.Peers().Direction(info.ID)
 	if err != nil {
```

### beacon-chain/rpc/prysm/node/handlers_test.go
```diff
@@ -220,6 +220,20 @@ func TestAddTrustedPeer_BadAddress(t *testing.T) {
 	assert.StringContains(t, "Could not derive peer info from multiaddress", e.Message)
 }
 
+func TestAddTrustedPeer_NoTransportAddress(t *testing.T) {
+	peerFetcher := &mockp2p.MockPeersProvider{}
+	peerFetcher.ClearPeers()
+	s := Server{PeersFetcher: peerFetcher}
+
+	body := bytes.NewBufferString(`{"addr":"/p2p/16Uiu2HAm1n583t4huDMMqEUUBuQs6bLts21mxCfX3tiqu9JfHvRJ"}`)
+	request := httptest.NewRequest("POST", "http://anything.is.fine", body)
+	writer := httptest.NewRecorder()
+	writer.Body = &bytes.Buffer{}
+
+	s.AddTrustedPeer(writer, request)
+	assert.Equal(t, http.StatusBadRequest, writer.Code)
+}
+
 func TestRemoveTrustedPeer(t *testing.T) {
 	peerFetcher := &mockp2p.MockPeersProvider{}
 	peerFetcher.ClearPeers()
```

### changelog/alleysira_fix-multiaddr-panic.md
```diff
@@ -0,0 +1,3 @@
+### Fixed
+
+- Fix panic when adding a trusted peer using a multiaddr with no transport address.
```
