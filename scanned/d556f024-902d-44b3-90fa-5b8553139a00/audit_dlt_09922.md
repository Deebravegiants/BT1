# [?] Merge pull request #322 from 2dvorak/fix-getblockheaders-overflow

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2025-05-29
Source: https://github.com/kaiachain/kaia/commit/67d0c4d72a24fd368299d8f448d41b32bcc70337
Type: security-commit

## Details
Merge pull request #322 from 2dvorak/fix-getblockheaders-overflow

node/cn: Fix overflows in `GetBlockHeaders`

## Patch
### node/cn/handler.go
```diff
@@ -799,13 +799,23 @@ func handleBlockHeadersRequestMsg(pm *ProtocolManager, p Peer, msg p2p.Msg) erro
 		switch {
 		case query.Origin.Hash != (common.Hash{}) && query.Reverse:
 			// Hash based traversal towards the genesis block
-			for i := 0; i < int(query.Skip)+1; i++ {
-				if header := pm.blockchain.GetHeader(query.Origin.Hash, number); header != nil {
-					query.Origin.Hash = header.ParentHash
-					number--
-				} else {
-					unknown = true
-					break
+			var (
+				current = origin.Number.Uint64()
+				next    = current - query.Skip - 1
+			)
+			if next >= current {
+				infos, _ := json.MarshalIndent(p.GetP2PPeer().Info(), "", "  ")
+				p.GetP2PPeer().Log().Warn("GetBlockHeaders skip underflow attack", "current", current, "skip", query.Skip, "next", next, "attacker", infos)
+				unknown = true
+			} else {
+				for i := 0; i < int(query.Skip)+1; i++ {
+					if header := pm.blockchain.GetHeader(query.Origin.Hash, number); header != nil {
+						query.Origin.Hash = header.ParentHash
+						number--
+					} else {
+						unknown = true
+						break
+					}
 				}
 			}
 		case query.Origin.Hash != (common.Hash{}) && !query.Reverse:
@@ -831,15 +841,22 @@ func handleBlockHeadersRequestMsg(pm *ProtocolManager, p Peer, msg p2p.Msg) erro
 			}
 		case query.Reverse:
 			// Number based traversal towards the genesis block
-			if query.Origin.Number >= query.Skip+1 {
-				query.Origin.Number -= query.Skip + 1
-			} else {
+			current := query.Origin.Number
+			ancestor := current - (query.Skip + 1)
+			if ancestor >= current { // check for underflow
 				unknown = true
+			} else {
+				query.Origin.Number = ancestor
 			}
-
 		case !query.Reverse:
 			// Number based traversal towards the leaf block
-			query.Origin.Number += query.Skip + 1
+			current := query.Origin.Number
+			next := current + query.Skip + 1
+			if next <= current { // check for overflow
+				unknown = true
+			} else {
+				query.Origin.Number = next
+			}
 		}
 	}
 	return p.SendBlockHeaders(headers)
```

### node/cn/handler_test.go
```diff
@@ -19,8 +19,10 @@
 package cn
 
 import (
+	"bytes"
 	"crypto/ecdsa"
 	"fmt"
+	"math"
 	"math/big"
 	"math/rand"
 	"testing"
@@ -29,8 +31,10 @@ import (
 	"github.com/golang/mock/gomock"
 	"github.com/kaiachain/kaia/blockchain"
 	"github.com/kaiachain/kaia/blockchain/types"
+	"github.com/kaiachain/kaia/blockchain/vm"
 	"github.com/kaiachain/kaia/common"
 	"github.com/kaiachain/kaia/consensus"
+	"github.com/kaiachain/kaia/consensus/gxhash"
 	consensusmocks "github.com/kaiachain/kaia/consensus/mocks"
 	"github.com/kaiachain/kaia/crypto"
 	"github.com/kaiachain/kaia/datasync/downloader"
@@ -39,6 +43,9 @@ import (
 	"github.com/kaiachain/kaia/networks/p2p/discover"
 	"github.com/kaiachain/kaia/node/cn/mocks"
 	"github.com/kaiachain/kaia/params"
+	"github.com/kaiachain/kaia/rlp"
+	"github.com/kaiachain/kaia/storage/database"
+	"github.com/kaiachain/kaia/storage/statedb"
 	workmocks "github.com/kaiachain/kaia/work/mocks"
 	"github.com/stretchr/testify/assert"
 )
@@ -1158,3 +1165,280 @@ func createAndRegisterPeers(mockCtrl *gomock.Controller, peers *peerSet) (*MockP
 
 	return cnPeer, pnPeer, enPeer
 }
+
+var (
+	// testKey is a private key to use for funding a tester account.
+	testKey, _ = crypto.HexToECDSA("b71c71a67e1177ad4e901695e1b4b9ee17ae16c6668d313eac2f96dbcda3f291")
+
+	// testAddr is the Ethereum address of the tester account.
+	testAddr = crypto.PubkeyToAddress(testKey.PublicKey)
+)
+
+func newTestBackendWithGenerator(blocks int, generator func(int, *blockchain.BlockGen)) (database.DBManager, *blockchain.BlockChain) {
+	var (
+		// Create a database pre-initialize with a genesis block
+		db     = database.NewMemoryDBManager()
+		config = params.TestChainConfig
+		engine = gxhash.NewFaker()
+	)
+
+	gspec := &blockchain.Genesis{
+		Config: config,
+		Alloc:  blockchain.GenesisAlloc{testAddr: {Balance: big.NewInt(100_000_000_000_000_000)}},
+	}
+	genesis := gspec.MustCommit(db)
+	cacheConfig := &blockchain.CacheConfig{
+		CacheSize:           512,
+		BlockInterval:       blockchain.DefaultBlockInterval,
+		TriesInMemory:       blockchain.DefaultTriesInMemory,
+		TrieNodeCacheConfig: statedb.GetEmptyTrieNodeCacheConfig(),
+		SnapshotCacheSize:   512,
+		ArchiveMode:         true, // Archive mode
+	}
+	chain, _ := blockchain.NewBlockChain(db, cacheConfig, config, engine, vm.Config{})
+
+	bs, _ := blockchain.GenerateChain(config, genesis, engine, db, blocks, generator)
+	if _, err := chain.InsertChain(bs); err != nil {
+		panic(err)
+	}
+	for i, block := range bs {
+		chain.StateCache().TrieDB().Commit(block.Root(), false, uint64(i))
+	}
+
+	return db, chain
+}
+
+// Tests that block headers can be retrieved from a remote chain based on user queries.
+func TestGetBlockHeaders(t *testing.T) {
+	t.Parallel()
+
+	db, backend := newTestBackendWithGenerator(downloader.MaxHeaderFetch+15, nil)
+	peer, _, net := newBasePeer()
+
+	// Create a "random" unknown hash for testing
+	var unknown common.Hash
+	for i := range unknown {
+		unknown[i] = byte(i)
+	}
+	getHashes := func(from, limit uint64) (hashes []common.Hash) {
+		for i := uint64(0); i < limit; i++ {
+			hashes = append(hashes, backend.GetBlockByNumber(from-1-i).Hash())
+		}
+		return hashes
+	}
+
+	limit := uint64(downloader.MaxHeaderFetch)
+	tests := []struct {
+		query  *getBlockHeadersData // The query to execute for header retrieval
+		expect []common.Hash        // The hashes of the block whose headers are expected
+	}{
+		// A single random block should be retrievable by hash
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Hash: backend.GetBlockByNumber(limit / 2).Hash()}, Amount: 1},
+			[]common.Hash{backend.GetBlockByNumber(limit / 2).Hash()},
+		},
+		// A single random block should be retrievable by number
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: limit / 2}, Amount: 1},
+			[]common.Hash{backend.GetBlockByNumber(limit / 2).Hash()},
+		},
+		// Multiple headers should be retrievable in both directions
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: limit / 2}, Amount: 3},
+			[]common.Hash{
+				backend.GetBlockByNumber(limit / 2).Hash(),
+				backend.GetBlockByNumber(limit/2 + 1).Hash(),
+				backend.GetBlockByNumber(limit/2 + 2).Hash(),
+			},
+		},
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: limit / 2}, Amount: 3, Reverse: true},
+			[]common.Hash{
+				backend.GetBlockByNumber(limit / 2).Hash(),
+				backend.GetBlockByNumber(limit/2 - 1).Hash(),
+				backend.GetBlockByNumber(limit/2 - 2).Hash(),
+			},
+		},
+		// Multiple headers with skip lists should be retrievable
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: limit / 2}, Skip: 3, Amount: 3},
+			[]common.Hash{
+				backend.GetBlockByNumber(limit / 2).Hash(),
+				backend.GetBlockByNumber(limit/2 + 4).Hash(),
+				backend.GetBlockByNumber(limit/2 + 8).Hash(),
+			},
+		},
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: limit / 2}, Skip: 3, Amount: 3, Reverse: true},
+			[]common.Hash{
+				backend.GetBlockByNumber(limit / 2).Hash(),
+				backend.GetBlockByNumber(limit/2 - 4).Hash(),
+				backend.GetBlockByNumber(limit/2 - 8).Hash(),
+			},
+		},
+		// The chain endpoints should be retrievable
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: 0}, Amount: 1},
+			[]common.Hash{backend.GetBlockByNumber(0).Hash()},
+		},
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: backend.CurrentBlock().Number().Uint64()}, Amount: 1},
+			[]common.Hash{backend.CurrentBlock().Hash()},
+		},
+		// If the peer requests a bit into the future, we deliver what we have
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: backend.CurrentBlock().Number().Uint64()}, Amount: 10},
+			[]common.Hash{backend.CurrentBlock().Hash()},
+		},
+		// Ensure protocol limits are honored
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: backend.CurrentBlock().Number().Uint64() - 1}, Amount: limit + 10, Reverse: true},
+			getHashes(backend.CurrentBlock().Number().Uint64(), limit),
+		},
+		// Check that requesting more than available is handled gracefully
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: backend.CurrentBlock().Number().Uint64() - 4}, Skip: 3, Amount: 3},
+			[]common.Hash{
+				backend.GetBlockByNumber(backend.CurrentBlock().Number().Uint64() - 4).Hash(),
+				backend.GetBlockByNumber(backend.CurrentBlock().Number().Uint64()).Hash(),
+			},
+		},
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: 4}, Skip: 3, Amount: 3, Reverse: true},
+			[]common.Hash{
+				backend.GetBlockByNumber(4).Hash(),
+				backend.GetBlockByNumber(0).Hash(),
+			},
+		},
+		// Check that requesting more than available is handled gracefully, even if mid skip
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: backend.CurrentBlock().Number().Uint64() - 4}, Skip: 2, Amount: 3},
+			[]common.Hash{
+				backend.GetBlockByNumber(backend.CurrentBlock().Number().Uint64() - 4).Hash(),
+				backend.GetBlockByNumber(backend.CurrentBlock().Number().Uint64() - 1).Hash(),
+			},
+		},
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: 4}, Skip: 2, Amount: 3, Reverse: true},
+			[]common.Hash{
+				backend.GetBlockByNumber(4).Hash(),
+				backend.GetBlockByNumber(1).Hash(),
+			},
+		},
+		// Check a corner case where requesting more can iterate past the endpoints
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: 2}, Amount: 5, Reverse: true},
+			[]common.Hash{
+				backend.GetBlockByNumber(2).Hash(),
+				backend.GetBlockByNumber(1).Hash(),
+				backend.GetBlockByNumber(0).Hash(),
+			},
+		},
+		// Check a corner case where skipping causes overflow with reverse=false
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: 1}, Amount: 2, Reverse: false, Skip: math.MaxUint64 - 1},
+			[]common.Hash{
+				backend.GetBlockByNumber(1).Hash(),
+			},
+		},
+		// Check a corner case where skipping causes overflow with reverse=true
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: 1}, Amount: 2, Reverse: true, Skip: math.MaxUint64 - 1},
+			[]common.Hash{
+				backend.GetBlockByNumber(1).Hash(),
+			},
+		},
+		// Check another corner case where skipping causes overflow with reverse=false
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: 1}, Amount: 2, Reverse: false, Skip: math.MaxUint64},
+			[]common.Hash{
+				backend.GetBlockByNumber(1).Hash(),
+			},
+		},
+		// Check another corner case where skipping causes overflow with reverse=true
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: 1}, Amount: 2, Reverse: true, Skip: math.MaxUint64},
+			[]common.Hash{
+				backend.GetBlockByNumber(1).Hash(),
+			},
+		},
+		// Check a corner case where skipping overflow loops back into the chain start
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Hash: backend.GetBlockByNumber(3).Hash()}, Amount: 2, Reverse: false, Skip: math.MaxUint64 - 1},
+			[]common.Hash{
+				backend.GetBlockByNumber(3).Hash(),
+			},
+		},
+		// Check a corner case where skipping overflow loops back to the same header
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Hash: backend.GetBlockByNumber(1).Hash()}, Amount: 2, Reverse: false, Skip: math.MaxUint64},
+			[]common.Hash{
+				backend.GetBlockByNumber(1).Hash(),
+			},
+		},
+		// Check that non existing headers aren't returned
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Hash: unknown}, Amount: 1},
+			[]common.Hash{},
+		},
+		{
+			&getBlockHeadersData{Origin: hashOrNumber{Number: backend.CurrentBlock().Number().Uint64() + 1}, Amount: 1},
+			[]common.Hash{},
+		},
+	}
+
+	pm, err := NewProtocolManager(params.TestChainConfig, downloader.FullSync, 1, nil, nil, backend.Engine(), backend, db, 1, common.ENDPOINTNODE, &Config{TxResendUseLegacy: false, TxResendInterval: 1, TxResendCount: 0})
+	if err != nil {
+		t.Fatal(err)
+	}
+
+	// Run each of the tests and verify the results against the chain
+	for i, tt := range tests {
+		// Collect the headers to expect in the response
+		var headers []*types.Header
+		for _, hash := range tt.expect {
+			headers = append(headers, backend.GetBlockByHash(hash).Header())
+		}
+		// Send the hash request and verify the response
+		_, r, _ := rlp.EncodeToReader(tt.query)
+		go func() {
+			handleBlockHeadersRequestMsg(pm, peer, p2p.Msg{Code: BlockHeadersRequestMsg, Payload: r})
+		}()
+		msg, err := net.ReadMsg()
+		if err != nil {
+			t.Fatal(err)
+		}
+		var receivedHeaders []*types.Header
+		if err := msg.Decode(&receivedHeaders); err != nil {
+			t.Fatal(err)
+		}
+		encodedHeaders, _ := rlp.EncodeToBytes(headers)
+		encodedReceivedHeaders, _ := rlp.EncodeToBytes(receivedHeaders)
+		if !bytes.Equal(encodedHeaders, encodedReceivedHeaders) {
+			t.Fatalf("test %d: headers mismatch, expected: %v, received: %v", i, headers, receivedHeaders)
+		}
+
+		// If the test used number origins, repeat with hashes as the origin too
+		if tt.query.Origin.Hash == (common.Hash{}) {
+			if origin := backend.GetBlockByNumber(tt.query.Origin.Number); origin != nil {
+				tt.query.Origin.Hash, tt.query.Origin.Number = origin.Hash(), 0
+				_, r, _ := rlp.EncodeToReader(tt.query)
+				go func() {
+					handleBlockHeadersRequestMsg(pm, peer, p2p.Msg{Code: BlockHeadersRequestMsg, Payload: r})
+				}()
+				msg, err := net.ReadMsg()
+				if err != nil {
+					t.Error(err)
+				}
+				if err := msg.Decode(&receivedHeaders); err != nil {
+					t.Fatal(err)
+				}
+				encodedHeaders, _ := rlp.EncodeToBytes(headers)
+				encodedReceivedHeaders, _ := rlp.EncodeToBytes(receivedHeaders)
+				if !bytes.Equal(encodedHeaders, encodedReceivedHeaders) {
+					t.Errorf("test %d: headers mismatch, expected: %v, received: %v", i, headers, receivedHeaders)
+				}
+			}
+		}
+	}
+}
```
