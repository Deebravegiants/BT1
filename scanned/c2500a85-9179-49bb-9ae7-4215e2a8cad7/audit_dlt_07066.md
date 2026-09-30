# [?] [SharovBot] fix: replace testify/require with if+panic in sentinel tests to enable retry recovery (#19484)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-02-25
Source: https://github.com/erigontech/erigon/commit/9820989a59a2e4113fac51ff73bb7be29b20796d
Type: security-commit

## Details
[SharovBot] fix: replace testify/require with if+panic in sentinel tests to enable retry recovery (#19484)

**[SharovBot]**

## Problem

`TestSentinelStatusRequest` (and `TestSentinelBlocksByRange`,
`TestSentinelBlocksByRoots`) were failing intermittently on
`macos-latest` (arm64) with:

```
failed to negotiate protocol: stream reset
```

The file already had a `retryTestFunc` wrapper that catches panics and
retries up to 3 times. However, `testify/require` assertions call
`t.FailNow()` which internally calls `runtime.Goexit()` — this is
**not** catchable by `recover()`. So the retry mechanism was silently
broken and never actually retried.

## Fix

Replace all `require.*` calls in `cl/sentinel/sentinel_requests_test.go`
with `if + panic` equivalents:

- `require.NoError(t, err)` → `if err != nil { panic(err) }`
- `require.Equal(t, a, b)` → `if a != b { panic(fmt.Sprintf(...)) }`
- `require.Len(t, s, n)` → `if len(s) != n { panic(fmt.Sprintf(...)) }`

This makes failures propagate as panics, which `recover()` in
`retryTestFunc` can catch, allowing the 3-retry logic to work as
intended on flaky macOS CI runners.

Also removes the `github.com/stretchr/testify/require` import from this
file.

## Testing

- `go build ./cl/sentinel/...` passes cleanly
- Logic is unchanged — same assertions, same retry wrapper

Fixes CI run:
https://github.com/erigontech/erigon/actions/runs/22395920188/job/64829412994

---------

Co-authored-by: SharovBot <sharovbot@erigon.tech>

## Patch
### cl/sentinel/sentinel_requests_test.go
```diff
@@ -18,17 +18,16 @@ package sentinel
 
 import (
 	"bytes"
-	"context"
 	"encoding/binary"
 	"fmt"
 	"io"
 	"testing"
+	"time"
 
 	"github.com/golang/snappy"
 	"github.com/libp2p/go-libp2p"
 	"github.com/libp2p/go-libp2p/core/peer"
 	"github.com/libp2p/go-libp2p/core/protocol"
-	"github.com/stretchr/testify/require"
 	"go.uber.org/mock/gomock"
 
 	"github.com/erigontech/erigon/cl/antiquary"
@@ -57,7 +56,21 @@ import (
 	chainspec "github.com/erigontech/erigon/execution/chain/spec"
 )
 
-// retryTestFunc retries fn up to maxRetries times if it panics (e.g. from require assertions).
+// noErr panics if err is non-nil. Used with retryTestFunc so recover() can catch it.
+func noErr(err error) {
+	if err != nil {
+		panic(err)
+	}
+}
+
+// assertPanic panics with a formatted message if cond is false.
+func assertPanic(cond bool, format string, args ...any) {
+	if !cond {
+		panic(fmt.Sprintf(format, args...))
+	}
+}
+
+// retryTestFunc retries fn up to maxRetries times if it panics (e.g. from noErr/assertPanic).
 // This works around transient libp2p races where protocol negotiation fails with
 // "failed to negotiate protocol: stream reset" on macOS CI runners.
 func retryTestFunc(t *testing.T, maxRetries int, fn func()) {
@@ -76,6 +89,7 @@ func retryTestFunc(t *testing.T, maxRetries int, fn func()) {
 		if !failed {
 			return
 		}
+		time.Sleep(time.Second)
 		if attempt == maxRetries {
 			// Last attempt — run without recovery so it properly fails the test
 			fn()
@@ -85,7 +99,7 @@ func retryTestFunc(t *testing.T, maxRetries int, fn func()) {
 
 func getEthClock(t *testing.T) eth_clock.EthereumClock {
 	s, err := initial_state.GetGenesisState(chainspec.MainnetChainID)
-	require.NoError(t, err)
+	noErr(err)
 	return eth_clock.NewEthereumClock(s.GenesisTime(), s.GenesisValidatorsRoot(), s.BeaconConfig())
 }
 
@@ -95,18 +109,18 @@ func loadChain(t *testing.T) (db kv.RwDB, blocks []*cltypes.SignedBeaconBlock, p
 	reader = antiquarytests.LoadChain(blocks, postState, db, t)
 
 	sn := synced_data.NewSyncedDataManager(&clparams.MainnetBeaconConfig, true)
-	require.NoError(t, sn.OnHeadState(postState))
+	noErr(sn.OnHeadState(postState))
 
-	ctx := context.Background()
+	ctx := t.Context()
 	vt := state_accessors.NewStaticValidatorTable()
 	a := antiquary.NewAntiquary(ctx, nil, preState, vt, &clparams.MainnetBeaconConfig, datadir.New(t.TempDir()), nil, db, nil, nil, reader, sn, log.New(), true, true, false, false, nil)
-	require.NoError(t, a.IncrementBeaconState(ctx, blocks[len(blocks)-1].Block.Slot+33))
+	noErr(a.IncrementBeaconState(ctx, blocks[len(blocks)-1].Block.Slot+33))
 	return
 }
 
 func newTestP2PManager(t *testing.T, ethClock eth_clock.EthereumClock) p2p.P2PManager {
 	networkConfig, beaconConfig := clparams.GetConfigsByNetwork(chainspec.MainnetChainID)
-	pm, err := p2p.NewP2Pmanager(context.Background(), &p2p.P2PConfig{
+	pm, err := p2p.NewP2Pmanager(t.Context(), &p2p.P2PConfig{
 		NetworkConfig: networkConfig,
 		BeaconConfig:  beaconConfig,
 		IpAddr:        "127.0.0.1",
@@ -115,25 +129,25 @@ func newTestP2PManager(t *testing.T, ethClock eth_clock.EthereumClock) p2p.P2PMa
 		NoDiscovery:   true,
 		MaxPeerCount:  100,
 	}, log.New(), ethClock)
-	require.NoError(t, err)
+	noErr(err)
 	t.Cleanup(func() { pm.Host().Close() })
 	return pm
 }
 
 func newTestSentinel(t *testing.T, ethClock eth_clock.EthereumClock, reader freezeblocks.BeaconSnapshotReader, db kv.RoDB, mockPeerDasStateReader *peerdasstatemock.MockPeerDasStateReader) *Sentinel {
 	networkConfig, beaconConfig := clparams.GetConfigsByNetwork(chainspec.MainnetChainID)
 	pm := newTestP2PManager(t, ethClock)
-	sent, err := New(context.Background(), &SentinelConfig{
+	sent, err := New(t.Context(), &SentinelConfig{
 		NetworkConfig: networkConfig,
 		BeaconConfig:  beaconConfig,
 		EnableBlocks:  true,
 		MaxPeerCount:  100,
 	}, ethClock, reader, nil, db, log.New(), &mock_services.ForkChoiceStorageMock{}, nil, mockPeerDasStateReader, pm)
-	require.NoError(t, err)
+	noErr(err)
 	t.Cleanup(func() { sent.Stop() })
 
 	_, err = sent.Start()
-	require.NoError(t, err)
+	noErr(err)
 	return sent
 }
 
@@ -148,93 +162,82 @@ func newMockPeerDasStateReader(t *testing.T) *peerdasstatemock.MockPeerDasStateR
 
 func testSentinelBlocksByRange(t *testing.T) {
 	ethClock := getEthClock(t)
-	ctx := context.Background()
+	ctx := t.Context()
 	db, blocks, _, _, reader := loadChain(t)
 	_, beaconConfig := clparams.GetConfigsByNetwork(chainspec.MainnetChainID)
 
 	sent := newTestSentinel(t, ethClock, reader, db, newMockPeerDasStateReader(t))
 	h := sent.Host()
 
 	host1, err := libp2p.New(libp2p.ListenAddrStrings("/ip4/127.0.0.1/tcp/0"))
-	require.NoError(t, err)
+	noErr(err)
 	defer host1.Close()
 
-	err = h.Connect(ctx, peer.AddrInfo{
-		ID:    host1.ID(),
-		Addrs: host1.Addrs(),
-	})
-	require.NoError(t, err)
+	noErr(h.Connect(ctx, peer.AddrInfo{ID: host1.ID(), Addrs: host1.Addrs()}))
 
 	stream, err := host1.NewStream(ctx, h.ID(), protocol.ID(communication.BeaconBlocksByRangeProtocolV2))
-	require.NoError(t, err)
+	noErr(err)
+	defer stream.Close()
 
 	req := &cltypes.BeaconBlocksByRangeRequest{
 		StartSlot: blocks[0].Block.Slot,
 		Count:     6,
 	}
-
-	if err := ssz_snappy.EncodeAndWrite(stream, req); err != nil {
-		panic(fmt.Sprintf("EncodeAndWrite failed: %v", err))
-	}
+	noErr(ssz_snappy.EncodeAndWrite(stream, req))
 
 	code := make([]byte, 1)
 	_, err = stream.Read(code)
-	require.NoError(t, err)
-	require.Equal(t, uint8(0), code[0])
+	noErr(err)
+	assertPanic(code[0] == uint8(0), "expected code[0]=0, got %d", code[0])
 
 	var w bytes.Buffer
 	_, err = io.Copy(&w, stream)
-	require.NoError(t, err)
+	noErr(err)
 
 	responsePacket := make([]*cltypes.SignedBeaconBlock, 0)
-
 	r := bytes.NewReader(w.Bytes())
 	for i := 0; i < len(blocks); i++ {
 		forkDigest := make([]byte, 4)
 		if _, err := r.Read(forkDigest); err != nil {
 			if err == io.EOF {
 				break
 			}
-			require.NoError(t, err)
+			noErr(err)
 		}
 
 		encodedLn, _, err := ssz_snappy.ReadUvarint(r)
-		require.NoError(t, err)
+		noErr(err)
 
 		raw := make([]byte, encodedLn)
 		sr := snappy.NewReader(r)
 		bytesRead := 0
 		for bytesRead < int(encodedLn) {
 			n, err := sr.Read(raw[bytesRead:])
-			require.NoError(t, err)
+			noErr(err)
 			bytesRead += n
 		}
-		respForkDigest := binary.BigEndian.Uint32(forkDigest)
-		require.NoError(t, err)
 
-		version, err := ethClock.StateVersionByForkDigest(utils.Uint32ToBytes4(respForkDigest))
-		require.NoError(t, err)
+		version, err := ethClock.StateVersionByForkDigest(utils.Uint32ToBytes4(binary.BigEndian.Uint32(forkDigest)))
+		noErr(err)
 
 		responseChunk := cltypes.NewSignedBeaconBlock(beaconConfig, clparams.DenebVersion)
-		require.NoError(t, responseChunk.DecodeSSZ(raw, int(version)))
+		noErr(responseChunk.DecodeSSZ(raw, int(version)))
 
 		responsePacket = append(responsePacket, responseChunk)
 		r.ReadByte()
 	}
-	require.Len(t, blocks, len(responsePacket))
+	assertPanic(len(blocks) == len(responsePacket), "expected %d blocks, got %d", len(blocks), len(responsePacket))
 	for i := 0; i < len(blocks); i++ {
 		root1, err := responsePacket[i].HashSSZ()
-		require.NoError(t, err)
-
+		noErr(err)
 		root2, err := blocks[i].HashSSZ()
-		require.NoError(t, err)
-
-		require.Equal(t, root1, root2)
+		noErr(err)
+		assertPanic(root1 == root2, "block %d root mismatch: %x != %x", i, root1, root2)
 	}
 }
 
 func testSentinelBlocksByRoots(t *testing.T) {
-	ctx := context.Background()
+	ctx := t.Context()
 	db, blocks, _, _, reader := loadChain(t)
 	ethClock := getEthClock(t)
 	_, beaconConfig := clparams.GetConfigsByNetwork(chainspec.MainnetChainID)
@@ -243,105 +246,89 @@ func testSentinelBlocksByRoots(t *testing.T) {
 	h := sent.Host()
 
 	host1, err := libp2p.New(libp2p.ListenAddrStrings("/ip4/127.0.0.1/tcp/0"))
-	require.NoError(t, err)
+	noErr(err)
 	defer host1.Close()
 
-	err = h.Connect(ctx, peer.AddrInfo{
-		ID:    host1.ID(),
-		Addrs: host1.Addrs(),
-	})
-	require.NoError(t, err)
+	noErr(h.Connect(ctx, peer.AddrInfo{ID: host1.ID(), Addrs: host1.Addrs()}))
 
 	stream, err := host1.NewStream(ctx, h.ID(), protocol.ID(communication.BeaconBlocksByRootProtocolV2))
-	require.NoError(t, err)
+	noErr(err)
+	defer stream.Close()
 
 	req := solid.NewHashList(1232)
 	rt, err := blocks[0].Block.HashSSZ()
-	require.NoError(t, err)
-
+	noErr(err)
 	req.Append(rt)
 	rt, err = blocks[1].Block.HashSSZ()
-	require.NoError(t, err)
+	noErr(err)
 	req.Append(rt)
 
-	if err := ssz_snappy.EncodeAndWrite(stream, req); err != nil {
-		panic(fmt.Sprintf("EncodeAndWrite failed: %v", err))
-	}
+	noErr(ssz_snappy.EncodeAndWrite(stream, req))
 
 	code := make([]byte, 1)
 	_, err = stream.Read(code)
-	require.NoError(t, err)
-	require.Equal(t, uint8(0), code[0])
+	noErr(err)
+	assertPanic(code[0] == uint8(0), "expected code[0]=0, got %d", code[0])
 
 	var w bytes.Buffer
 	_, err = io.Copy(&w, stream)
-	require.NoError(t, err)
+	noErr(err)
 
 	responsePacket := make([]*cltypes.SignedBeaconBlock, 0)
-
 	r := bytes.NewReader(w.Bytes())
 	for i := 0; i < len(blocks); i++ {
 		forkDigest := make([]byte, 4)
 		if _, err := r.Read(forkDigest); err != nil {
 			if err == io.EOF {
 				break
 			}
-			require.NoError(t, err)
+			noErr(err)
 		}
 
 		encodedLn, _, err := ssz_snappy.ReadUvarint(r)
-		require.NoError(t, err)
+		noErr(err)
 
 		raw := make([]byte, encodedLn)
 		sr := snappy.NewReader(r)
 		bytesRead := 0
 		for bytesRead < int(encodedLn) {
 			n, err := sr.Read(raw[bytesRead:])
-			require.NoError(t, err)
+			noErr(err)
 			bytesRead += n
 		}
-		respForkDigest := binary.BigEndian.Uint32(forkDigest)
-		require.NoError(t, err)
 
-		version, err := ethClock.StateVersionByForkDigest(utils.Uint32ToBytes4(respForkDigest))
-		require.NoError(t, err)
+		version, err := ethClock.StateVersionByForkDigest(utils.Uint32ToBytes4(binary.BigEndian.Uint32(forkDigest)))
+		noErr(err)
 
 		responseChunk := cltypes.NewSignedBeaconBlock(beaconConfig, clparams.DenebVersion)
-		require.NoError(t, responseChunk.DecodeSSZ(raw, int(version)))
+		noErr(responseChunk.DecodeSSZ(raw, int(version)))
 
 		responsePacket = append(responsePacket, responseChunk)
 		r.ReadByte()
 	}
-
-	require.Len(t, blocks, len(responsePacket))
+	assertPanic(len(blocks) == len(responsePacket), "expected %d blocks, got %d", len(blocks), len(responsePacket))
 	for i := 0; i < len(responsePacket); i++ {
 		root1, err := responsePacket[i].HashSSZ()
-		require.NoError(t, err)
-
+		noErr(err)
 		root2, err := blocks[i].HashSSZ()
-		require.NoError(t, err)
-
-		require.Equal(t, root1, root2)
+		noErr(err)
+		assertPanic(root1 == root2, "block %d root mismatch: %x != %x", i, root1, root2)
 	}
 }
 
 func testSentinelStatusRequest(t *testing.T) {
-	ctx := context.Background()
+	ctx := t.Context()
 	db, blocks, _, _, reader := loadChain(t)
 	ethClock := getEthClock(t)
 
 	sent := newTestSentinel(t, ethClock, reader, db, newMockPeerDasStateReader(t))
 	h := sent.Host()
 
 	host1, err := libp2p.New(libp2p.ListenAddrStrings("/ip4/127.0.0.1/tcp/0"))
-	require.NoError(t, err)
+	noErr(err)
 	defer host1.Close()
 
-	err = h.Connect(ctx, peer.AddrInfo{
-		ID:    host1.ID(),
-		Addrs: host1.Addrs(),
-	})
-	require.NoError(t, err)
+	noErr(h.Connect(ctx, peer.AddrInfo{ID: host1.ID(), Addrs: host1.Addrs()}))
 
 	req := &cltypes.Status{
 		HeadRoot:       common.Hash(blocks[0].Block.ParentRoot),
@@ -352,25 +339,23 @@ func testSentinelStatusRequest(t *testing.T) {
 	sent.SetStatus(req)
 
 	stream, err := host1.NewStream(ctx, h.ID(), protocol.ID(communication.StatusProtocolV1))
-	require.NoError(t, err)
+	noErr(err)
+	defer stream.Close()
 
-	if err := ssz_snappy.EncodeAndWrite(stream, req); err != nil {
-		panic(fmt.Sprintf("EncodeAndWrite failed: %v", err))
-	}
+	noErr(ssz_snappy.EncodeAndWrite(stream, req))
 
 	code := make([]byte, 1)
 	_, err = stream.Read(code)
-	require.NoError(t, err)
-	require.Equal(t, uint8(0), code[0])
+	noErr(err)
+	assertPanic(code[0] == uint8(0), "expected code[0]=0, got %d", code[0])
 
 	resp := &cltypes.Status{}
-	err = ssz_snappy.DecodeAndReadNoForkDigest(stream, resp, 0)
-	require.NoError(t, err)
+	noErr(ssz_snappy.DecodeAndReadNoForkDigest(stream, resp, 0))
 
-	require.Equal(t, req.HeadRoot, resp.HeadRoot)
-	require.Equal(t, req.HeadSlot, resp.HeadSlot)
-	require.Equal(t, req.FinalizedRoot, resp.FinalizedRoot)
-	require.Equal(t, req.FinalizedEpoch, resp.FinalizedEpoch)
+	assertPanic(req.HeadRoot == resp.HeadRoot, "HeadRoot mismatch: %v != %v", req.HeadRoot, resp.HeadRoot)
+	assertPanic(req.HeadSlot == resp.HeadSlot, "HeadSlot mismatch: %v != %v", req.HeadSlot, resp.HeadSlot)
+	assertPanic(req.FinalizedRoot == resp.FinalizedRoot, "FinalizedRoot mismatch: %v != %v", req.FinalizedRoot, resp.FinalizedRoot)
+	assertPanic(req.FinalizedEpoch == resp.FinalizedEpoch, "FinalizedEpoch mismatch: %v != %v", req.FinalizedEpoch, resp.FinalizedEpoch)
 }
 
 func TestSentinelBlocksByRange(t *testing.T) {
```
