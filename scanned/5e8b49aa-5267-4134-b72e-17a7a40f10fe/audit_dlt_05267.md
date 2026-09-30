# [?] eth/protocols: pre-decode item count validation (CVE-2026-26313 mitigation)

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2026-03-27
Source: https://github.com/etclabscore/core-geth/commit/7940b28167825389fd510f97e5e29c7eb6ed770c
Type: security-commit

## Details
eth/protocols: pre-decode item count validation (CVE-2026-26313 mitigation)

Add item count validation before full RLP message decoding in both eth
and snap protocol handlers. This prevents memory amplification attacks
where compact RLP-encoded items expand into large in-memory objects.

The check uses rlp.CountValues on the raw payload to count items
without allocating memory for decoded objects. Messages exceeding the
expected limits are rejected before any decoding occurs.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### eth/protocols/eth/handler.go
```diff
@@ -17,7 +17,9 @@
 package eth
 
 import (
+	"bytes"
 	"fmt"
+	"io"
 	"math/big"
 	"time"
 
@@ -29,6 +31,7 @@ import (
 	"github.com/ethereum/go-ethereum/p2p/enode"
 	"github.com/ethereum/go-ethereum/p2p/enr"
 	"github.com/ethereum/go-ethereum/params/types/ctypes"
+	"github.com/ethereum/go-ethereum/rlp"
 )
 
 const (
@@ -184,6 +187,60 @@ var eth68 = map[uint64]msgHandler{
 	PooledTransactionsMsg:         handlePooledTransactions,
 }
 
+// responseItemLimits defines the maximum number of items allowed in response
+// messages. This prevents memory amplification attacks (CVE-2026-26313) where
+// compact RLP-encoded items expand into large in-memory objects during decoding.
+type responseLimit struct {
+	maxItems int
+	wrapped  bool // true if the packet has a RequestId wrapper
+}
+
+var responseItemLimits = map[uint64]responseLimit{
+	BlockHeadersMsg:       {maxItems: maxHeadersServe, wrapped: true},
+	BlockBodiesMsg:        {maxItems: maxBodiesServe, wrapped: true},
+	ReceiptsMsg:           {maxItems: maxReceiptsServe, wrapped: true},
+	PooledTransactionsMsg: {maxItems: maxHeadersServe * 4, wrapped: true},
+	TransactionsMsg:       {maxItems: maxHeadersServe * 4, wrapped: false},
+}
+
+// checkResponseItems reads the message payload into a buffer, counts the number
+// of RLP items in the response list, and rejects messages that exceed maxItems.
+// The msg.Payload is replaced with a bytes.Reader so subsequent Decode calls work.
+func checkResponseItems(msg *p2p.Msg, limit responseLimit) error {
+	buf := make([]byte, msg.Size)
+	if _, err := io.ReadFull(msg.Payload, buf); err != nil {
+		return err
+	}
+	msg.Payload = bytes.NewReader(buf)
+
+	content, _, err := rlp.SplitList(buf)
+	if err != nil {
+		return err
+	}
+	var itemsContent []byte
+	if limit.wrapped {
+		// Skip RequestId (first element of the outer list)
+		_, _, rest, err := rlp.Split(content)
+		if err != nil {
+			return err
+		}
+		itemsContent, _, err = rlp.SplitList(rest)
+		if err != nil {
+			return err
+		}
+	} else {
+		itemsContent = content
+	}
+	count, err := rlp.CountValues(itemsContent)
+	if err != nil {
+		return err
+	}
+	if count > limit.maxItems {
+		return fmt.Errorf("%w: too many items in response: %d > %d", errDecode, count, limit.maxItems)
+	}
+	return nil
+}
+
 // handleMessage is invoked whenever an inbound message is received from a remote
 // peer. The remote connection is torn down upon returning any error.
 func handleMessage(backend Backend, peer *Peer) error {
@@ -197,6 +254,13 @@ func handleMessage(backend Backend, peer *Peer) error {
 	}
 	defer msg.Discard()
 
+	// Pre-decode item count validation to prevent memory amplification attacks.
+	if limit, ok := responseItemLimits[msg.Code]; ok {
+		if err := checkResponseItems(&msg, limit); err != nil {
+			return err
+		}
+	}
+
 	var handlers = eth68
 
 	// Track the amount of time it takes to serve the request and run the handler
```

### eth/protocols/eth/handler_cve_test.go
```diff
@@ -0,0 +1,117 @@
+// Copyright 2026 The go-ethereum Authors
+// This file is part of the go-ethereum library.
+//
+// The go-ethereum library is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// The go-ethereum library is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with the go-ethereum library. If not, see <http://www.gnu.org/licenses/>.
+
+package eth
+
+import (
+	"bytes"
+	"testing"
+
+	"github.com/ethereum/go-ethereum/core/types"
+	"github.com/ethereum/go-ethereum/p2p"
+	"github.com/ethereum/go-ethereum/rlp"
+)
+
+// TestCheckResponseItems_CVE_2026_26313 verifies that the pre-decode item count
+// validation rejects messages with too many items, preventing memory amplification
+// attacks (CVE-2026-26313).
+func TestCheckResponseItems_CVE_2026_26313(t *testing.T) {
+	// Build a wrapped packet (BlockHeadersPacket) with N minimal headers.
+	buildHeadersMsg := func(n int) p2p.Msg {
+		headers := make([]*types.Header, n)
+		for i := range headers {
+			headers[i] = &types.Header{}
+		}
+		pkt := &BlockHeadersPacket{
+			RequestId:           1,
+			BlockHeadersRequest: BlockHeadersRequest(headers),
+		}
+		payload, err := rlp.EncodeToBytes(pkt)
+		if err != nil {
+			t.Fatal(err)
+		}
+		return p2p.Msg{
+			Code:    BlockHeadersMsg,
+			Size:    uint32(len(payload)),
+			Payload: bytes.NewReader(payload),
+		}
+	}
+
+	// Build a bare packet (TransactionsPacket) with N minimal transactions.
+	buildTxsMsg := func(n int) p2p.Msg {
+		txs := make(TransactionsPacket, n)
+		for i := range txs {
+			txs[i] = types.NewTx(&types.LegacyTx{})
+		}
+		payload, err := rlp.EncodeToBytes(txs)
+		if err != nil {
+			t.Fatal(err)
+		}
+		return p2p.Msg{
+			Code:    TransactionsMsg,
+			Size:    uint32(len(payload)),
+			Payload: bytes.NewReader(payload),
+		}
+	}
+
+	t.Run("wrapped packet within limit passes", func(t *testing.T) {
+		msg := buildHeadersMsg(maxHeadersServe)
+		limit := responseItemLimits[BlockHeadersMsg]
+		if err := checkResponseItems(&msg, limit); err != nil {
+			t.Fatalf("expected no error for %d headers, got: %v", maxHeadersServe, err)
+		}
+	})
+
+	t.Run("wrapped packet exceeding limit rejected", func(t *testing.T) {
+		msg := buildHeadersMsg(maxHeadersServe + 1)
+		limit := responseItemLimits[BlockHeadersMsg]
+		if err := checkResponseItems(&msg, limit); err == nil {
+			t.Fatalf("expected error for %d headers (limit %d), got nil", maxHeadersServe+1, maxHeadersServe)
+		}
+	})
+
+	t.Run("bare packet within limit passes", func(t *testing.T) {
+		msg := buildTxsMsg(100)
+		limit := responseItemLimits[TransactionsMsg]
+		if err := checkResponseItems(&msg, limit); err != nil {
+			t.Fatalf("expected no error for 100 txs, got: %v", err)
+		}
+	})
+
+	t.Run("bare packet exceeding limit rejected", func(t *testing.T) {
+		msg := buildTxsMsg(maxHeadersServe*4 + 1)
+		limit := responseItemLimits[TransactionsMsg]
+		if err := checkResponseItems(&msg, limit); err == nil {
+			t.Fatalf("expected error for %d txs (limit %d), got nil", maxHeadersServe*4+1, maxHeadersServe*4)
+		}
+	})
+
+	t.Run("payload still decodable after check", func(t *testing.T) {
+		msg := buildHeadersMsg(10)
+		limit := responseItemLimits[BlockHeadersMsg]
+		if err := checkResponseItems(&msg, limit); err != nil {
+			t.Fatalf("unexpected error: %v", err)
+		}
+		// Verify the payload can still be decoded after the check
+		res := new(BlockHeadersPacket)
+		if err := msg.Decode(res); err != nil {
+			t.Fatalf("failed to decode after check: %v", err)
+		}
+		if len(res.BlockHeadersRequest) != 10 {
+			t.Fatalf("expected 10 headers, got %d", len(res.BlockHeadersRequest))
+		}
+	})
+}
```

### eth/protocols/snap/handler.go
```diff
@@ -19,6 +19,7 @@ package snap
 import (
 	"bytes"
 	"fmt"
+	"io"
 	"time"
 
 	"github.com/ethereum/go-ethereum/common"
@@ -29,6 +30,7 @@ import (
 	"github.com/ethereum/go-ethereum/p2p"
 	"github.com/ethereum/go-ethereum/p2p/enode"
 	"github.com/ethereum/go-ethereum/p2p/enr"
+	"github.com/ethereum/go-ethereum/rlp"
 	"github.com/ethereum/go-ethereum/trie"
 	"github.com/ethereum/go-ethereum/trie/trienode"
 )
@@ -126,6 +128,47 @@ func Handle(backend Backend, peer *Peer) error {
 	}
 }
 
+// snapResponseLimits defines the maximum number of items allowed in snap
+// response messages to prevent memory amplification attacks (CVE-2026-26313).
+var snapResponseLimits = map[uint64]int{
+	AccountRangeMsg:  maxCodeLookups * 10, // generous limit for account ranges
+	StorageRangesMsg: maxCodeLookups * 10,
+	ByteCodesMsg:     maxCodeLookups,
+	TrieNodesMsg:     maxTrieNodeLookups,
+}
+
+// checkSnapResponseItems reads the message payload into a buffer, counts items
+// in the first list field after the ID, and rejects messages exceeding maxItems.
+func checkSnapResponseItems(msg *p2p.Msg, maxItems int) error {
+	buf := make([]byte, msg.Size)
+	if _, err := io.ReadFull(msg.Payload, buf); err != nil {
+		return err
+	}
+	msg.Payload = bytes.NewReader(buf)
+
+	content, _, err := rlp.SplitList(buf)
+	if err != nil {
+		return err
+	}
+	// Skip ID (first element), then count items in the second element (the data list)
+	_, _, rest, err := rlp.Split(content)
+	if err != nil {
+		return err
+	}
+	itemsContent, _, err := rlp.SplitList(rest)
+	if err != nil {
+		return err
+	}
+	count, err := rlp.CountValues(itemsContent)
+	if err != nil {
+		return err
+	}
+	if count > maxItems {
+		return fmt.Errorf("%w: too many items in response: %d > %d", errDecode, count, maxItems)
+	}
+	return nil
+}
+
 // HandleMessage is invoked whenever an inbound message is received from a
 // remote peer on the `snap` protocol. The remote connection is torn down upon
 // returning any error.
@@ -139,6 +182,14 @@ func HandleMessage(backend Backend, peer *Peer) error {
 		return fmt.Errorf("%w: %v > %v", errMsgTooLarge, msg.Size, maxMessageSize)
 	}
 	defer msg.Discard()
+
+	// Pre-decode item count validation to prevent memory amplification attacks.
+	if maxItems, ok := snapResponseLimits[msg.Code]; ok {
+		if err := checkSnapResponseItems(&msg, maxItems); err != nil {
+			return err
+		}
+	}
+
 	start := time.Now()
 	// Track the amount of time it takes to serve the request and run the handler
 	if metrics.Enabled {
```
