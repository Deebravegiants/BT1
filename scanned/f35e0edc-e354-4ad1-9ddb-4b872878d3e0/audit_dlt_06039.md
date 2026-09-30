# [?] fix: harden deserialization and message handlers against panics (#4844)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2026-06-03
Source: https://github.com/iotexproject/iotex-core/commit/83768641751bec0c72bab14d9c2af30299a9b6e2
Type: security-commit

## Details
fix: harden deserialization and message handlers against panics (#4844)

* fix: harden deserialization and message handlers against panics

Replace five panic-prone paths reachable from peer-controlled or untrusted
input with explicit error returns / safe fallbacks:

- action.envelope.LoadProto: return ErrInvalidAct on unknown TxType instead
  of panicking on TxType >= 5.
- evm.ExtractRevertMessage: bound-check the Error(string) ABI payload and
  reject non-UTF-8 messages; fall back to hex on malformed input.
- evm.StateDBAdapter.AddLog: guard the in-contract-transfer topic check
  against empty topics.
- chainservice.Filter / ReportFullness: reject blocks with nil Header or
  nil Header.Core before dereferencing Height.
- endorsement.Endorsement.LoadProto: return an error on nil proto instead
  of panicking before signature/delegate verification.

Add unit tests covering each new error path.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

* fix: address three HIGH-severity peer-reachable attack vectors

Findings #6, #7, #9 from the security audit, all read-verified:

#6 nodeinfo: HandleNodeInfo dereferenced msg.Info without a nil check, so
any peer could crash a node by broadcasting NODE_INFO with Info=nil.
Now guarded; non-panic test added.

#7 actsync: RequestActionsFromNeighbors had no upper bound on the number
of in-flight requests, letting a peer drown a node in outbound traffic.
Cap added; tests cover cap respected under flood, dedup must not
double-count, concurrent flood respects cap.

#9 server/itx: admin mux (/pause, /unpause, /producer-keys, pprof) was
bound to 0.0.0.0, letting any peer that could reach the admin port halt
block production with an unauthenticated POST to /pause. Now bound to
127.0.0.1.

(Finding #8 — actpool cross-shard eviction — has been moved to a
separate PR for independent review.)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

* fix(evm): reject malformed revert payloads instead of silent hex fallback

Change ExtractRevertMessage signature to (string, error) and propagate
the error from ExecuteContract so a tx with a malformed Error(string)
revert payload invalidates the action rather than landing with a junk
hex string in the receipt. erigonstore callers swallow the error with a
local hex fallback since they already return vm.ErrExecutionReverted to
their caller.

Drop the utf8.Valid gate — honest contracts can revert with non-UTF-8
bytes, so rejecting on that would fork the chain on legitimate input.
Added a regression test pinning the non-UTF-8 happy path.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

### action/envelope.go
```diff
@@ -6,7 +6,6 @@
 package action
 
 import (
-	"fmt"
 	"math/big"
 
 	"github.com/ethereum/go-ethereum/common"
@@ -320,7 +319,7 @@ func (elp *envelope) loadProtoTxCommon(pbAct *iotextypes.ActionCore) error {
 			elp.common = &tx
 		}
 	default:
-		panic(fmt.Sprintf("unsupported action type = %d", pbAct.TxType))
+		return errors.Wrapf(ErrInvalidAct, "unsupported tx type = %d", pbAct.TxType)
 	}
 	return err
 }
```

### action/envelope_test.go
```diff
@@ -140,6 +140,14 @@ func createEnvelope(chainID uint32) (Envelope, *Transfer) {
 	return evlp, tsf
 }
 
+func TestEnvelope_LoadProto_UnsupportedTxType(t *testing.T) {
+	req := require.New(t)
+	evlp := &envelope{}
+	err := evlp.LoadProto(&iotextypes.ActionCore{TxType: 5})
+	req.Error(err)
+	req.ErrorIs(err, ErrInvalidAct)
+}
+
 func TestEnvelope_Hash(t *testing.T) {
 	r := require.New(t)
 	blob := createTestBlobTxData()
```

### action/protocol/execution/evm/evm.go
```diff
@@ -8,7 +8,6 @@ package evm
 import (
 	"bytes"
 	"context"
-	"encoding/hex"
 	"math"
 	"math/big"
 	"time"
@@ -374,7 +373,11 @@ func ExecuteContract(
 
 	if ps.featureCtx.SetRevertMessageToReceipt && receipt.Status == uint64(iotextypes.ReceiptStatus_ErrExecutionReverted) && len(retval) >= 4 && bytes.Equal(retval[:4], _revertSelector) {
 		// in case of the execution revert error, parse the retVal and add to receipt
-		receipt.SetExecutionRevertMsg(ExtractRevertMessage(retval))
+		msg, err := ExtractRevertMessage(retval)
+		if err != nil {
+			return nil, nil, err
+		}
+		receipt.SetExecutionRevertMsg(msg)
 	}
 	return retval, receipt, nil
 }
@@ -963,18 +966,21 @@ func SimulateAndCollectAccessList(
 	return stateDB.AccessedSlots(), nil
 }
 
-// ExtractRevertMessage extracts the revert message from the return value
-func ExtractRevertMessage(ret []byte) string {
-	if len(ret) < 4 {
-		return hex.EncodeToString(ret)
-	}
-	if !bytes.Equal(ret[:4], _revertSelector) {
-		return hex.EncodeToString(ret)
+// ExtractRevertMessage extracts the revert message from the return value.
+// Returns an error if the payload is not a well-formed Error(string) revert.
+func ExtractRevertMessage(ret []byte) (string, error) {
+	if len(ret) < 4 || !bytes.Equal(ret[:4], _revertSelector) {
+		return "", errors.New("malformed revert payload: missing Error(string) selector")
 	}
 	data := ret[4:]
+	if len(data) < 64 {
+		return "", errors.New("malformed revert payload: data shorter than offset+length header")
+	}
 	msgLength := byteutil.BytesToUint64BigEndian(data[56:64])
-	revertMsg := string(data[64 : 64+msgLength])
-	return revertMsg
+	if msgLength > uint64(len(data)-64) {
+		return "", errors.New("malformed revert payload: declared length exceeds available data")
+	}
+	return string(data[64 : 64+msgLength]), nil
 }
 
 func validateAuthorization(evm *vm.EVM, sdb stateDB, auth *types.SetCodeAuthorization, isBlackListed IsBlackListedFunc, blockHeight uint64) (authority common.Address, err error) {
```

### action/protocol/execution/evm/evm_test.go
```diff
@@ -6,8 +6,10 @@
 package evm
 
 import (
+	"bytes"
 	"context"
 	"crypto/ecdsa"
+	"encoding/binary"
 	"errors"
 	"math/big"
 	"testing"
@@ -606,3 +608,91 @@ func TestEIP7702BlacklistLogic(t *testing.T) {
 	r.NoError(err, "converting authority to io address should succeed")
 	r.Equal(ioAddr.String(), convertedAddr.String(), "converted address should match expected io address")
 }
+
+func TestExtractRevertMessage(t *testing.T) {
+	r := require.New(t)
+
+	// Build a well-formed Error(string) payload for the given message.
+	wellFormed := func(msg string) []byte {
+		out := append([]byte{}, _revertSelector...)
+		offset := make([]byte, 32)
+		offset[31] = 0x20
+		out = append(out, offset...)
+		length := make([]byte, 32)
+		binary.BigEndian.PutUint64(length[24:32], uint64(len(msg)))
+		out = append(out, length...)
+		data := []byte(msg)
+		if pad := len(data) % 32; pad != 0 {
+			data = append(data, make([]byte, 32-pad)...)
+		}
+		return append(out, data...)
+	}
+
+	for _, tc := range []struct {
+		name    string
+		in      []byte
+		want    string
+		wantErr bool
+	}{
+		{"nil", nil, "", true},
+		{"shorter than selector", []byte{0x01, 0x02}, "", true},
+		{"non-revert prefix", []byte{0x01, 0x02, 0x03, 0x04, 0x05}, "", true},
+		{
+			"selector only, truncated length offset",
+			append(append([]byte{}, _revertSelector...), bytes.Repeat([]byte{0xff}, 50)...),
+			"", true,
+		},
+		{
+			"msgLength exceeds remaining payload",
+			func() []byte {
+				out := append([]byte{}, _revertSelector...)
+				out = append(out, bytes.Repeat([]byte{0x00}, 32)...) // offset
+				length := make([]byte, 32)
+				binary.BigEndian.PutUint64(length[24:32], 1<<20) // claim 1MB message
+				out = append(out, length...)
+				out = append(out, []byte("short")...) // but only provide 5 bytes
+				return out
+			}(),
+			"", true,
+		},
+		{"well-formed hello", wellFormed("hello"), "hello", false},
+		{"well-formed empty", wellFormed(""), "", false},
+		{"well-formed with emoji", wellFormed("nope 🚫"), "nope 🚫", false},
+		{
+			// Regression guard: utf8.Valid check was intentionally removed so
+			// honest-but-non-UTF-8 reverts remain consensus-compatible.
+			"well-formed but non-UTF-8 string",
+			func() []byte {
+				out := append([]byte{}, _revertSelector...)
+				offset := make([]byte, 32)
+				offset[31] = 0x20
+				out = append(out, offset...)
+				length := make([]byte, 32)
+				length[31] = 0x02
+				out = append(out, length...)
+				out = append(out, 0xff, 0xfe)
+				out = append(out, make([]byte, 30)...)
+				return out
+			}(),
+			"\xff\xfe", false,
+		},
+		{
+			// Boundary: msgLength exactly equals len(data)-64.
+			"msgLength exactly fills payload",
+			wellFormed("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"), // 32 bytes, no padding required
+			"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", false,
+		},
+	} {
+		t.Run(tc.name, func(t *testing.T) {
+			r.NotPanics(func() {
+				got, err := ExtractRevertMessage(tc.in)
+				if tc.wantErr {
+					r.Error(err)
+				} else {
+					r.NoError(err)
+				}
+				r.Equal(tc.want, got)
+			})
+		})
+	}
+}
```

### action/protocol/execution/evm/evmstatedbadapter.go
```diff
@@ -926,7 +926,7 @@ func (stateDB *StateDBAdapter) AddLog(evmLog *types.Log) {
 		copy(topic[:], evmTopic.Bytes())
 		topics = append(topics, topic)
 	}
-	if topics[0] == _inContractTransfer {
+	if len(topics) > 0 && topics[0] == _inContractTransfer {
 		if len(topics) != 3 {
 			log.T(stateDB.ctx).Panic("Invalid in contract transfer topics")
 		}
```

### actsync/actionsync.go
```diff
@@ -3,6 +3,7 @@ package actsync
 import (
 	"context"
 	"sync"
+	"sync/atomic"
 	"time"
 
 	"github.com/iotexproject/go-pkgs/hash"
@@ -33,6 +34,7 @@ type (
 	ActionSync struct {
 		lifecycle.Readiness
 		actions  sync.Map
+		pending  atomic.Int64 // number of live entries in `actions`; bounded by cfg.Size
 		syncChan chan hash.Hash256
 		wg       sync.WaitGroup
 		helper   *Helper
@@ -104,15 +106,24 @@ func (as *ActionSync) RequestAction(_ context.Context, hash hash.Hash256) {
 	if !as.IsReady() {
 		return
 	}
+	// Bound the pending request set: a peer can flood us with forged ACTION_HASH
+	// messages that never resolve, so cap the live map by cfg.Size. Reserve the
+	// slot atomically before touching the map to prevent OOM and unbounded
+	// per-hash unicast amplification by triggerSync.
+	if as.pending.Add(1) > int64(as.cfg.Size) {
+		as.pending.Add(-1)
+		counterMtc.WithLabelValues("capacityExceeded").Inc()
+		log.L().Debug("action sync request capacity exceeded", log.Hex("hash", hash[:]))
+		return
+	}
 	// check if the action is already requested
-	_, ok := as.actions.LoadOrStore(hash, &actionMsg{})
-	if ok {
+	if _, ok := as.actions.LoadOrStore(hash, &actionMsg{}); ok {
+		as.pending.Add(-1)
 		log.L().Debug("Action already requested", log.Hex("hash", hash[:]))
 		return
 	}
 	log.L().Debug("Requesting action", log.Hex("hash", hash[:]))
 	as.trigger(hash)
-	return
 }
 
 // ReceiveAction receives an action
@@ -121,7 +132,9 @@ func (as *ActionSync) ReceiveAction(_ context.Context, hash hash.Hash256) {
 		return
 	}
 	log.L().Debug("received action", log.Hex("hash", hash[:]))
-	as.actions.Delete(hash)
+	if _, loaded := as.actions.LoadAndDelete(hash); loaded {
+		as.pending.Add(-1)
+	}
 }
 
 func (as *ActionSync) sync() {
```

### actsync/actionsync_test.go
```diff
@@ -126,6 +126,102 @@ func TestActionSync(t *testing.T) {
 			r.False(ok, "action should be removed after received")
 		}
 	})
+	t.Run("capacityBound", func(t *testing.T) {
+		// Forged-hash flood: every request is for a unique hash that never
+		// resolves via ReceiveAction. The live map must not grow past cfg.Size.
+		const cap = 8
+		bs := NewActionSync(Config{
+			Size:     cap,
+			Interval: time.Hour, // disable trigger churn for the duration of this test
+		}, &Helper{
+			P2PNeighbor: func() ([]peer.AddrInfo, error) {
+				return neighbors, nil
+			},
+			UnicastOutbound: func(_ context.Context, _ peer.AddrInfo, _ proto.Message) error {
+				return nil
+			},
+		})
+		r.NoError(bs.Start(context.Background()))
+		defer func() { r.NoError(bs.Stop(context.Background())) }()
+		for i := 0; i < cap*4; i++ {
+			bs.RequestAction(context.Background(), hash.Hash256b([]byte{0xff, byte(i), byte(i >> 8)}))
+		}
+		r.Equal(int64(cap), bs.pending.Load(), "pending count must not exceed configured cap")
+		stored := 0
+		bs.actions.Range(func(_, _ any) bool { stored++; return true })
+		r.Equal(cap, stored, "live entries must match the cap")
+		// ReceiveAction on a hash we already stored must drop the counter so a new request can land.
+		var sample hash.Hash256
+		bs.actions.Range(func(k, _ any) bool { sample = k.(hash.Hash256); return false })
+		bs.ReceiveAction(context.Background(), sample)
+		r.Equal(int64(cap-1), bs.pending.Load(), "ReceiveAction must release the slot")
+		bs.RequestAction(context.Background(), hash.Hash256b([]byte("fresh")))
+		r.Equal(int64(cap), bs.pending.Load(), "freed slot can be reused")
+	})
+	t.Run("duplicateRequestDoesNotDoubleCount", func(t *testing.T) {
+		// LoadOrStore must observe an existing entry and refund the slot, otherwise a
+		// peer that repeats the same forged hash would still grow the counter and
+		// eventually wedge the pool at the cap with one real hash.
+		bs := NewActionSync(Config{
+			Size:     4,
+			Interval: time.Hour,
+		}, &Helper{
+			P2PNeighbor: func() ([]peer.AddrInfo, error) {
+				return neighbors, nil
+			},
+			UnicastOutbound: func(_ context.Context, _ peer.AddrInfo, _ proto.Message) error {
+				return nil
+			},
+		})
+		r.NoError(bs.Start(context.Background()))
+		defer func() { r.NoError(bs.Stop(context.Background())) }()
+		dup := hash.Hash256b([]byte("dup"))
+		for i := 0; i < 50; i++ {
+			bs.RequestAction(context.Background(), dup)
+		}
+		r.Equal(int64(1), bs.pending.Load(), "repeated requests for the same hash must collapse to one slot")
+		// ReceiveAction on an unknown hash must not decrement.
+		bs.ReceiveAction(context.Background(), hash.Hash256b([]byte("missing")))
+		r.Equal(int64(1), bs.pending.Load(), "ReceiveAction for an unknown hash must be a no-op for the counter")
+		bs.ReceiveAction(context.Background(), dup)
+		r.Equal(int64(0), bs.pending.Load())
+	})
+	t.Run("concurrentFloodRespectsCap", func(t *testing.T) {
+		// Under contention the atomic reserve+undo must hold the cap exactly;
+		// otherwise a peer can race the check and force the map past the limit.
+		const cap = 16
+		bs := NewActionSync(Config{
+			Size:     cap,
+			Interval: time.Hour,
+		}, &Helper{
+			P2PNeighbor: func() ([]peer.AddrInfo, error) {
+				return neighbors, nil
+			},
+			UnicastOutbound: func(_ context.Context, _ peer.AddrInfo, _ proto.Message) error {
+				return nil
+			},
+		})
+		r.NoError(bs.Start(context.Background()))
+		defer func() { r.NoError(bs.Stop(context.Background())) }()
+		const goroutines = 32
+		const perG = 200
+		wg := sync.WaitGroup{}
+		for g := 0; g < goroutines; g++ {
+			wg.Add(1)
+			go func(g int) {
+				defer wg.Done()
+				for k := 0; k < perG; k++ {
+					bs.RequestAction(context.Background(), hash.Hash256b([]byte{byte(g), byte(k), byte(k >> 8)}))
+				}
+			}(g)
+		}
+		wg.Wait()
+		r.LessOrEqual(bs.pending.Load(), int64(cap), "pending must never exceed configured cap, even under contention")
+		stored := 0
+		bs.actions.Range(func(_, _ any) bool { stored++; return true })
+		r.LessOrEqual(stored, cap, "live entries must never exceed the cap")
+		r.EqualValues(stored, bs.pending.Load(), "counter and map size must agree")
+	})
 	t.Run("requestWhenStopping", func(t *testing.T) {
 		count := atomic.Int32{}
 		as := NewActionSync(Config{
```

### chainservice/chainservice.go
```diff
@@ -136,7 +136,7 @@ func (cs *ChainService) Filter(messageType iotexrpc.MessageType, msg proto.Messa
 		return true
 	}
 	blk, ok := msg.(*iotextypes.Block)
-	if !ok || blk == nil {
+	if !ok || blk == nil || blk.Header == nil || blk.Header.Core == nil {
 		return false
 	}
 	if blk.Header.Core.Height > atomic.LoadUint64(&cs.lastReceivedBlockHeight) {
@@ -156,7 +156,7 @@ func (cs *ChainService) ReportFullness(_ context.Context, messageType iotexrpc.M
 	switch messageType {
 	case iotexrpc.MessageType_BLOCK:
 		blk, ok := msg.(*iotextypes.Block)
-		if !ok || blk == nil {
+		if !ok || blk == nil || blk.Header == nil || blk.Header.Core == nil {
 			return
 		}
 		if blk.Header.Core.Height > atomic.LoadUint64(&cs.lastReceivedBlockHeight) {
```

### chainservice/chainservice_test.go
```diff
@@ -0,0 +1,59 @@
+// Copyright (c) 2024 IoTeX Foundation
+// This source code is provided 'as is' and no warranties are given as to title or non-infringement, merchantability
+// or fitness for purpose and, to the extent permitted by law, all liability for your use of the code is disclaimed.
+// This source code is governed by Apache License 2.0 that can be found in the LICENSE file.
+
+package chainservice
+
+import (
+	"testing"
+
+	"github.com/iotexproject/iotex-proto/golang/iotexrpc"
+	"github.com/iotexproject/iotex-proto/golang/iotextypes"
+	"github.com/stretchr/testify/require"
+)
+
+func TestChainService_Filter_NilHeader(t *testing.T) {
+	r := require.New(t)
+	cs := &ChainService{}
+
+	cases := []struct {
+		name string
+		msg  *iotextypes.Block
+	}{
+		{"nil block", nil},
+		{"nil header", &iotextypes.Block{Header: nil}},
+		{"nil header core", &iotextypes.Block{Header: &iotextypes.BlockHeader{Core: nil}}},
+	}
+	for _, tc := range cases {
+		t.Run(tc.name, func(t *testing.T) {
+			r.NotPanics(func() {
+				r.False(cs.Filter(iotexrpc.MessageType_BLOCK, tc.msg, 10))
+			})
+		})
+	}
+
+	// Non-BLOCK messages always pass without inspecting payload.
+	r.True(cs.Filter(iotexrpc.MessageType_ACTION, nil, 10))
+}
+
+func TestChainService_ReportFullness_NilHeader(t *testing.T) {
+	r := require.New(t)
+	cs := &ChainService{}
+
+	cases := []struct {
+		name string
+		msg  *iotextypes.Block
+	}{
+		{"nil block", nil},
+		{"nil header", &iotextypes.Block{Header: nil}},
+		{"nil header core", &iotextypes.Block{Header: &iotextypes.BlockHeader{Core: nil}}},
+	}
+	for _, tc := range cases {
+		t.Run(tc.name, func(t *testing.T) {
+			r.NotPanics(func() {
+				cs.ReportFullness(nil, iotexrpc.MessageType_BLOCK, tc.msg, 0.5)
+			})
+		})
+	}
+}
```

### endorsement/endorsement.go
```diff
@@ -6,6 +6,7 @@
 package endorsement
 
 import (
+	"errors"
 	"time"
 
 	"github.com/iotexproject/go-pkgs/crypto"
@@ -128,6 +129,9 @@ func (en *Endorsement) Proto() *iotextypes.Endorsement {
 
 // LoadProto converts a protobuf message to endorsement
 func (en *Endorsement) LoadProto(ePb *iotextypes.Endorsement) (err error) {
+	if ePb == nil {
+		return errors.New("nil endorsement")
+	}
 	if err = ePb.Timestamp.CheckValid(); err != nil {
 		return err
 	}
```

### endorsement/endorsement_test.go
```diff
@@ -0,0 +1,52 @@
+// Copyright (c) 2024 IoTeX Foundation
+// This source code is provided 'as is' and no warranties are given as to title or non-infringement, merchantability
+// or fitness for purpose and, to the extent permitted by law, all liability for your use of the code is disclaimed.
+// This source code is governed by Apache License 2.0 that can be found in the LICENSE file.
+
+package endorsement
+
+import (
+	"bytes"
+	"testing"
+	"time"
+
+	"github.com/iotexproject/iotex-proto/golang/iotextypes"
+	"github.com/stretchr/testify/require"
+
+	"github.com/iotexproject/iotex-core/v2/test/identityset"
+)
+
+func TestEndorsement_LoadProto_Nil(t *testing.T) {
+	r := require.New(t)
+	en := &Endorsement{}
+	r.NotPanics(func() {
+		err := en.LoadProto(nil)
+		r.Error(err)
+	})
+}
+
+func TestEndorsement_LoadProto_RoundTrip(t *testing.T) {
+	r := require.New(t)
+	priKey := identityset.PrivateKey(0)
+	sig := []byte("signature")
+	now := time.Now()
+
+	original := NewEndorsement(now, priKey.PublicKey(), sig)
+	pb := original.Proto()
+
+	loaded := &Endorsement{}
+	r.NoError(loaded.LoadProto(pb))
+	r.True(now.Equal(loaded.Timestamp()))
+	r.Equal(priKey.PublicKey().HexString(), loaded.Endorser().HexString())
+	r.Equal(0, bytes.Compare(sig, loaded.Signature()))
+}
+
+func TestEndorsement_LoadProto_InvalidEndorser(t *testing.T) {
+	r := require.New(t)
+	en := &Endorsement{}
+	err := en.LoadProto(&iotextypes.Endorsement{
+		// Timestamp left zero is valid (encodes epoch); Endorser bytes are garbage.
+		Endorser: []byte{0x01, 0x02, 0x03},
+	})
+	r.Error(err)
+}
```

### nodeinfo/manager.go
```diff
@@ -145,6 +145,11 @@ func (dm *InfoManager) MayHaveBlock(peerID string, start uint64) bool {
 // HandleNodeInfo handle node info message
 func (dm *InfoManager) HandleNodeInfo(ctx context.Context, peerID string, msg *iotextypes.NodeInfo) {
 	log.L().Debug("nodeinfo manager handle node info")
+	// reject malformed messages from peers before dereferencing inner fields
+	if msg == nil || msg.Info == nil {
+		log.L().Warn("nodeinfo manager received malformed node info", zap.String("peerID", peerID))
+		return
+	}
 	// recover pubkey
 	hash := hashNodeInfo(msg.Info)
 	pubKey, err := crypto.RecoverPubkey(hash[:], msg.Signature)
```
