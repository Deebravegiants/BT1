# [?] les: fix crasher in NodeInfo when running as server (#17419)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2018-08-17
Source: https://github.com/celo-org/celo-blockchain/commit/2695fa2213fe5010a80970bca1078834662d5972
Type: security-commit

## Details
les: fix crasher in NodeInfo when running as server (#17419)

* les: fix crasher in NodeInfo when running as server

The ProtocolManager computes CHT and Bloom trie roots by asking the
indexers for their current head. It tried to get the indexers from
LesOdr, but no LesOdr instance is created in server mode.

Attempt to fix this by moving the indexers, protocol creation and
NodeInfo to a new lesCommons struct which is embedded into both server
and client.

All this setup code should really be cleaned up, but this is just a
hotfix so we have to do that some other time.

* les: fix commons protocol maker

## Patch
### les/backend.go
```diff
@@ -34,7 +34,6 @@ import (
 	"github.com/ethereum/go-ethereum/eth/downloader"
 	"github.com/ethereum/go-ethereum/eth/filters"
 	"github.com/ethereum/go-ethereum/eth/gasprice"
-	"github.com/ethereum/go-ethereum/ethdb"
 	"github.com/ethereum/go-ethereum/event"
 	"github.com/ethereum/go-ethereum/internal/ethapi"
 	"github.com/ethereum/go-ethereum/light"
@@ -47,26 +46,24 @@ import (
 )
 
 type LightEthereum struct {
-	config *eth.Config
+	lesCommons
 
 	odr         *LesOdr
 	relay       *LesTxRelay
 	chainConfig *params.ChainConfig
 	// Channel for shutting down the service
 	shutdownChan chan bool
+
 	// Handlers
-	peers           *peerSet
-	txPool          *light.TxPool
-	blockchain      *light.LightChain
-	protocolManager *ProtocolManager
-	serverPool      *serverPool
-	reqDist         *requestDistributor
-	retriever       *retrieveManager
-	// DB interfaces
-	chainDb ethdb.Database // Block chain database
-
-	bloomRequests                              chan chan *bloombits.Retrieval // Channel receiving bloom data retrieval requests
-	bloomIndexer, chtIndexer, bloomTrieIndexer *core.ChainIndexer
+	peers      *peerSet
+	txPool     *light.TxPool
+	blockchain *light.LightChain
+	serverPool *serverPool
+	reqDist    *requestDistributor
+	retriever  *retrieveManager
+
+	bloomRequests chan chan *bloombits.Retrieval // Channel receiving bloom data retrieval requests
+	bloomIndexer  *core.ChainIndexer
 
 	ApiBackend *LesApiBackend
 
@@ -95,9 +92,11 @@ func New(ctx *node.ServiceContext, config *eth.Config) (*LightEthereum, error) {
 	quitSync := make(chan struct{})
 
 	leth := &LightEthereum{
-		config:         config,
+		lesCommons: lesCommons{
+			chainDb: chainDb,
+			config:  config,
+		},
 		chainConfig:    chainConfig,
-		chainDb:        chainDb,
 		eventMux:       ctx.EventMux,
 		peers:          peers,
 		reqDist:        newRequestDistributor(peers, quitSync),
@@ -112,10 +111,12 @@ func New(ctx *node.ServiceContext, config *eth.Config) (*LightEthereum, error) {
 	leth.relay = NewLesTxRelay(peers, leth.reqDist)
 	leth.serverPool = newServerPool(chainDb, quitSync, &leth.wg)
 	leth.retriever = newRetrieveManager(peers, leth.reqDist, leth.serverPool)
+
 	leth.odr = NewLesOdr(chainDb, leth.retriever)
 	leth.chtIndexer = light.NewChtIndexer(chainDb, true, leth.odr)
 	leth.bloomTrieIndexer = light.NewBloomTrieIndexer(chainDb, true, leth.odr)
 	leth.odr.SetIndexers(leth.chtIndexer, leth.bloomTrieIndexer, leth.bloomIndexer)
+
 	// Note: NewLightChain adds the trusted checkpoint so it needs an ODR with
 	// indexers already set but not started yet
 	if leth.blockchain, err = light.NewLightChain(leth.odr, leth.chainConfig, leth.engine); err != nil {
@@ -125,6 +126,7 @@ func New(ctx *node.ServiceContext, config *eth.Config) (*LightEthereum, error) {
 	leth.bloomIndexer.AddChildIndexer(leth.bloomTrieIndexer)
 	leth.chtIndexer.Start(leth.blockchain)
 	leth.bloomIndexer.Start(leth.blockchain)
+
 	// Rewind the chain in case of an incompatible config upgrade.
 	if compat, ok := genesisErr.(*params.ConfigCompatError); ok {
 		log.Warn("Rewinding chain to upgrade configuration", "err", compat)
@@ -133,7 +135,7 @@ func New(ctx *node.ServiceContext, config *eth.Config) (*LightEthereum, error) {
 	}
 
 	leth.txPool = light.NewTxPool(leth.chainConfig, leth.blockchain, leth.relay)
-	if leth.protocolManager, err = NewProtocolManager(leth.chainConfig, true, ClientProtocolVersions, config.NetworkId, leth.eventMux, leth.engine, leth.peers, leth.blockchain, nil, chainDb, leth.odr, leth.relay, leth.serverPool, quitSync, &leth.wg); err != nil {
+	if leth.protocolManager, err = NewProtocolManager(leth.chainConfig, true, config.NetworkId, leth.eventMux, leth.engine, leth.peers, leth.blockchain, nil, chainDb, leth.odr, leth.relay, leth.serverPool, quitSync, &leth.wg); err != nil {
 		return nil, err
 	}
 	leth.ApiBackend = &LesApiBackend{leth, nil}
@@ -215,14 +217,14 @@ func (s *LightEthereum) ResetWithGenesisBlock(gb *types.Block) {
 func (s *LightEthereum) BlockChain() *light.LightChain      { return s.blockchain }
 func (s *LightEthereum) TxPool() *light.TxPool              { return s.txPool }
 func (s *LightEthereum) Engine() consensus.Engine           { return s.engine }
-func (s *LightEthereum) LesVersion() int                    { return int(s.protocolManager.SubProtocols[0].Version) }
+func (s *LightEthereum) LesVersion() int                    { return int(ClientProtocolVersions[0]) }
 func (s *LightEthereum) Downloader() *downloader.Downloader { return s.protocolManager.downloader }
 func (s *LightEthereum) EventMux() *event.TypeMux           { return s.eventMux }
 
 // Protocols implements node.Service, returning all the currently configured
 // network protocols to start.
 func (s *LightEthereum) Protocols() []p2p.Protocol {
-	return s.protocolManager.SubProtocols
+	return s.makeProtocols(ClientProtocolVersions)
 }
 
 // Start implements node.Service, starting all internal goroutines needed by the
@@ -242,12 +244,8 @@ func (s *LightEthereum) Start(srvr *p2p.Server) error {
 // Ethereum protocol.
 func (s *LightEthereum) Stop() error {
 	s.odr.Stop()
-	if s.bloomIndexer != nil {
-		s.bloomIndexer.Close()
-	}
-	if s.chtIndexer != nil {
-		s.chtIndexer.Close()
-	}
+	s.bloomIndexer.Close()
+	s.chtIndexer.Close()
 	s.blockchain.Stop()
 	s.protocolManager.Stop()
 	s.txPool.Stop()
```

### les/commons.go
```diff
@@ -0,0 +1,106 @@
+// Copyright 2018 The go-ethereum Authors
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
+package les
+
+import (
+	"fmt"
+	"math/big"
+
+	"github.com/ethereum/go-ethereum/common"
+	"github.com/ethereum/go-ethereum/core"
+	"github.com/ethereum/go-ethereum/eth"
+	"github.com/ethereum/go-ethereum/ethdb"
+	"github.com/ethereum/go-ethereum/light"
+	"github.com/ethereum/go-ethereum/p2p"
+	"github.com/ethereum/go-ethereum/p2p/discover"
+	"github.com/ethereum/go-ethereum/params"
+)
+
+// lesCommons contains fields needed by both server and client.
+type lesCommons struct {
+	config                       *eth.Config
+	chainDb                      ethdb.Database
+	protocolManager              *ProtocolManager
+	chtIndexer, bloomTrieIndexer *core.ChainIndexer
+}
+
+// NodeInfo represents a short summary of the Ethereum sub-protocol metadata
+// known about the host peer.
+type NodeInfo struct {
+	Network    uint64                  `json:"network"`    // Ethereum network ID (1=Frontier, 2=Morden, Ropsten=3, Rinkeby=4)
+	Difficulty *big.Int                `json:"difficulty"` // Total difficulty of the host's blockchain
+	Genesis    common.Hash             `json:"genesis"`    // SHA3 hash of the host's genesis block
+	Config     *params.ChainConfig     `json:"config"`     // Chain configuration for the fork rules
+	Head       common.Hash             `json:"head"`       // SHA3 hash of the host's best owned block
+	CHT        light.TrustedCheckpoint `json:"cht"`        // Trused CHT checkpoint for fast catchup
+}
+
+// makeProtocols creates protocol descriptors for the given LES versions.
+func (c *lesCommons) makeProtocols(versions []uint) []p2p.Protocol {
+	protos := make([]p2p.Protocol, len(versions))
+	for i, version := range versions {
+		version := version
+		protos[i] = p2p.Protocol{
+			Name:     "les",
+			Version:  version,
+			Length:   ProtocolLengths[version],
+			NodeInfo: c.nodeInfo,
+			Run: func(p *p2p.Peer, rw p2p.MsgReadWriter) error {
+				return c.protocolManager.runPeer(version, p, rw)
+			},
+			PeerInfo: func(id discover.NodeID) interface{} {
+				if p := c.protocolManager.peers.Peer(fmt.Sprintf("%x", id[:8])); p != nil {
+					return p.Info()
+				}
+				return nil
+			},
+		}
+	}
+	return protos
+}
+
+// nodeInfo retrieves some protocol metadata about the running host node.
+func (c *lesCommons) nodeInfo() interface{} {
+	var cht light.TrustedCheckpoint
+	sections, _, sectionHead := c.chtIndexer.Sections()
+	sections2, _, sectionHead2 := c.bloomTrieIndexer.Sections()
+	if sections2 < sections {
+		sections = sections2
+		sectionHead = sectionHead2
+	}
+	if sections > 0 {
+		sectionIndex := sections - 1
+		cht = light.TrustedCheckpoint{
+			SectionIdx:  sectionIndex,
+			SectionHead: sectionHead,
+			CHTRoot:     light.GetChtRoot(c.chainDb, sectionIndex, sectionHead),
+			BloomRoot:   light.GetBloomTrieRoot(c.chainDb, sectionIndex, sectionHead),
+		}
+	}
+
+	chain := c.protocolManager.blockchain
+	head := chain.CurrentHeader()
+	hash := head.Hash()
+	return &NodeInfo{
+		Network:    c.config.NetworkId,
+		Difficulty: chain.GetTd(hash, head.Number.Uint64()),
+		Genesis:    chain.Genesis().Hash(),
+		Config:     chain.Config(),
+		Head:       chain.CurrentHeader().Hash(),
+		CHT:        cht,
+	}
+}
```

### les/handler.go
```diff
@@ -20,7 +20,6 @@ package les
 import (
 	"encoding/binary"
 	"encoding/json"
-	"errors"
 	"fmt"
 	"math/big"
 	"net"
@@ -40,7 +39,6 @@ import (
 	"github.com/ethereum/go-ethereum/light"
 	"github.com/ethereum/go-ethereum/log"
 	"github.com/ethereum/go-ethereum/p2p"
-	"github.com/ethereum/go-ethereum/p2p/discover"
 	"github.com/ethereum/go-ethereum/p2p/discv5"
 	"github.com/ethereum/go-ethereum/params"
 	"github.com/ethereum/go-ethereum/rlp"
@@ -65,10 +63,6 @@ const (
 	disableClientRemovePeer = false
 )
 
-// errIncompatibleConfig is returned if the requested protocols and configs are
-// not compatible (low protocol version restrictions and high requirements).
-var errIncompatibleConfig = errors.New("incompatible configuration")
-
 func errResp(code errCode, format string, v ...interface{}) error {
 	return fmt.Errorf("%v - %v", code, fmt.Sprintf(format, v...))
 }
@@ -115,8 +109,6 @@ type ProtocolManager struct {
 	peers      *peerSet
 	maxPeers   int
 
-	SubProtocols []p2p.Protocol
-
 	eventMux *event.TypeMux
 
 	// channels for fetcher, syncer, txsyncLoop
@@ -131,7 +123,7 @@ type ProtocolManager struct {
 
 // NewProtocolManager returns a new ethereum sub protocol manager. The Ethereum sub protocol manages peers capable
 // with the ethereum network.
-func NewProtocolManager(chainConfig *params.ChainConfig, lightSync bool, protocolVersions []uint, networkId uint64, mux *event.TypeMux, engine consensus.Engine, peers *peerSet, blockchain BlockChain, txpool txPool, chainDb ethdb.Database, odr *LesOdr, txrelay *LesTxRelay, serverPool *serverPool, quitSync chan struct{}, wg *sync.WaitGroup) (*ProtocolManager, error) {
+func NewProtocolManager(chainConfig *params.ChainConfig, lightSync bool, networkId uint64, mux *event.TypeMux, engine consensus.Engine, peers *peerSet, blockchain BlockChain, txpool txPool, chainDb ethdb.Database, odr *LesOdr, txrelay *LesTxRelay, serverPool *serverPool, quitSync chan struct{}, wg *sync.WaitGroup) (*ProtocolManager, error) {
 	// Create the protocol manager with the base fields
 	manager := &ProtocolManager{
 		lightSync:   lightSync,
@@ -155,54 +147,6 @@ func NewProtocolManager(chainConfig *params.ChainConfig, lightSync bool, protoco
 		manager.reqDist = odr.retriever.dist
 	}
 
-	// Initiate a sub-protocol for every implemented version we can handle
-	manager.SubProtocols = make([]p2p.Protocol, 0, len(protocolVersions))
-	for _, version := range protocolVersions {
-		// Compatible, initialize the sub-protocol
-		version := version // Closure for the run
-		manager.SubProtocols = append(manager.SubProtocols, p2p.Protocol{
-			Name:    "les",
-			Version: version,
-			Length:  ProtocolLengths[version],
-			Run: func(p *p2p.Peer, rw p2p.MsgReadWriter) error {
-				var entry *poolEntry
-				peer := manager.newPeer(int(version), networkId, p, rw)
-				if manager.serverPool != nil {
-					addr := p.RemoteAddr().(*net.TCPAddr)
-					entry = manager.serverPool.connect(peer, addr.IP, uint16(addr.Port))
-				}
-				peer.poolEntry = entry
-				select {
-				case manager.newPeerCh <- peer:
-					manager.wg.Add(1)
-					defer manager.wg.Done()
-					err := manager.handle(peer)
-					if entry != nil {
-						manager.serverPool.disconnect(entry)
-					}
-					return err
-				case <-manager.quitSync:
-					if entry != nil {
-						manager.serverPool.disconnect(entry)
-					}
-					return p2p.DiscQuitting
-				}
-			},
-			NodeInfo: func() interface{} {
-				return manager.NodeInfo()
-			},
-			PeerInfo: func(id discover.NodeID) interface{} {
-				if p := manager.peers.Peer(fmt.Sprintf("%x", id[:8])); p != nil {
-					return p.Info()
-				}
-				return nil
-			},
-		})
-	}
-	if len(manager.SubProtocols) == 0 {
-		return nil, errIncompatibleConfig
-	}
-
 	removePeer := manager.removePeer
 	if disableClientRemovePeer {
 		removePeer = func(id string) {}
@@ -262,6 +206,32 @@ func (pm *ProtocolManager) Stop() {
 	log.Info("Light Ethereum protocol stopped")
 }
 
+// runPeer is the p2p protocol run function for the given version.
+func (pm *ProtocolManager) runPeer(version uint, p *p2p.Peer, rw p2p.MsgReadWriter) error {
+	var entry *poolEntry
+	peer := pm.newPeer(int(version), pm.networkId, p, rw)
+	if pm.serverPool != nil {
+		addr := p.RemoteAddr().(*net.TCPAddr)
+		entry = pm.serverPool.connect(peer, addr.IP, uint16(addr.Port))
+	}
+	peer.poolEntry = entry
+	select {
+	case pm.newPeerCh <- peer:
+		pm.wg.Add(1)
+		defer pm.wg.Done()
+		err := pm.handle(peer)
+		if entry != nil {
+			pm.serverPool.disconnect(entry)
+		}
+		return err
+	case <-pm.quitSync:
+		if entry != nil {
+			pm.serverPool.disconnect(entry)
+		}
+		return p2p.DiscQuitting
+	}
+}
+
 func (pm *ProtocolManager) newPeer(pv int, nv uint64, p *p2p.Peer, rw p2p.MsgReadWriter) *peer {
 	return newPeer(pv, nv, p, newMeteredMsgWriter(rw))
 }
@@ -1203,50 +1173,6 @@ func (pm *ProtocolManager) txStatus(hashes []common.Hash) []txStatus {
 	return stats
 }
 
-// NodeInfo represents a short summary of the Ethereum sub-protocol metadata
-// known about the host peer.
-type NodeInfo struct {
-	Network    uint64                  `json:"network"`    // Ethereum network ID (1=Frontier, 2=Morden, Ropsten=3, Rinkeby=4)
-	Difficulty *big.Int                `json:"difficulty"` // Total difficulty of the host's blockchain
-	Genesis    common.Hash             `json:"genesis"`    // SHA3 hash of the host's genesis block
-	Config     *params.ChainConfig     `json:"config"`     // Chain configuration for the fork rules
-	Head       common.Hash             `json:"head"`       // SHA3 hash of the host's best owned block
-	CHT        light.TrustedCheckpoint `json:"cht"`        // Trused CHT checkpoint for fast catchup
-}
-
-// NodeInfo retrieves some protocol metadata about the running host node.
-func (self *ProtocolManager) NodeInfo() *NodeInfo {
-	head := self.blockchain.CurrentHeader()
-	hash := head.Hash()
-
-	var cht light.TrustedCheckpoint
-
-	sections, _, sectionHead := self.odr.ChtIndexer().Sections()
-	sections2, _, sectionHead2 := self.odr.BloomTrieIndexer().Sections()
-	if sections2 < sections {
-		sections = sections2
-		sectionHead = sectionHead2
-	}
-	if sections > 0 {
-		sectionIndex := sections - 1
-		cht = light.TrustedCheckpoint{
-			SectionIdx:  sectionIndex,
-			SectionHead: sectionHead,
-			CHTRoot:     light.GetChtRoot(self.chainDb, sectionIndex, sectionHead),
-			BloomRoot:   light.GetBloomTrieRoot(self.chainDb, sectionIndex, sectionHead),
-		}
-	}
-
-	return &NodeInfo{
-		Network:    self.networkId,
-		Difficulty: self.blockchain.GetTd(hash, head.Number.Uint64()),
-		Genesis:    self.blockchain.Genesis().Hash(),
-		Config:     self.blockchain.Config(),
-		Head:       hash,
-		CHT:        cht,
-	}
-}
-
 // downloaderPeerNotify implements peerSetNotify
 type downloaderPeerNotify ProtocolManager
 
```

### les/helper_test.go
```diff
@@ -172,18 +172,12 @@ func newTestProtocolManager(lightSync bool, blocks int, generator func(int, *cor
 		chain = blockchain
 	}
 
-	var protocolVersions []uint
-	if lightSync {
-		protocolVersions = ClientProtocolVersions
-	} else {
-		protocolVersions = ServerProtocolVersions
-	}
-	pm, err := NewProtocolManager(gspec.Config, lightSync, protocolVersions, NetworkId, evmux, engine, peers, chain, nil, db, odr, nil, nil, make(chan struct{}), new(sync.WaitGroup))
+	pm, err := NewProtocolManager(gspec.Config, lightSync, NetworkId, evmux, engine, peers, chain, nil, db, odr, nil, nil, make(chan struct{}), new(sync.WaitGroup))
 	if err != nil {
 		return nil, err
 	}
 	if !lightSync {
-		srv := &LesServer{protocolManager: pm}
+		srv := &LesServer{lesCommons: lesCommons{protocolManager: pm}}
 		pm.server = srv
 
 		srv.defParams = &flowcontrol.ServerParams{
```

### les/server.go
```diff
@@ -38,21 +38,19 @@ import (
 )
 
 type LesServer struct {
-	config          *eth.Config
-	protocolManager *ProtocolManager
-	fcManager       *flowcontrol.ClientManager // nil if our node is client only
-	fcCostStats     *requestCostStats
-	defParams       *flowcontrol.ServerParams
-	lesTopics       []discv5.Topic
-	privateKey      *ecdsa.PrivateKey
-	quitSync        chan struct{}
-
-	chtIndexer, bloomTrieIndexer *core.ChainIndexer
+	lesCommons
+
+	fcManager   *flowcontrol.ClientManager // nil if our node is client only
+	fcCostStats *requestCostStats
+	defParams   *flowcontrol.ServerParams
+	lesTopics   []discv5.Topic
+	privateKey  *ecdsa.PrivateKey
+	quitSync    chan struct{}
 }
 
 func NewLesServer(eth *eth.Ethereum, config *eth.Config) (*LesServer, error) {
 	quitSync := make(chan struct{})
-	pm, err := NewProtocolManager(eth.BlockChain().Config(), false, ServerProtocolVersions, config.NetworkId, eth.EventMux(), eth.Engine(), newPeerSet(), eth.BlockChain(), eth.TxPool(), eth.ChainDb(), nil, nil, nil, quitSync, new(sync.WaitGroup))
+	pm, err := NewProtocolManager(eth.BlockChain().Config(), false, config.NetworkId, eth.EventMux(), eth.Engine(), newPeerSet(), eth.BlockChain(), eth.TxPool(), eth.ChainDb(), nil, nil, nil, quitSync, new(sync.WaitGroup))
 	if err != nil {
 		return nil, err
 	}
@@ -63,13 +61,17 @@ func NewLesServer(eth *eth.Ethereum, config *eth.Config) (*LesServer, error) {
 	}
 
 	srv := &LesServer{
-		config:           config,
-		protocolManager:  pm,
-		quitSync:         quitSync,
-		lesTopics:        lesTopics,
-		chtIndexer:       light.NewChtIndexer(eth.ChainDb(), false, nil),
-		bloomTrieIndexer: light.NewBloomTrieIndexer(eth.ChainDb(), false, nil),
+		lesCommons: lesCommons{
+			config:           config,
+			chainDb:          eth.ChainDb(),
+			chtIndexer:       light.NewChtIndexer(eth.ChainDb(), false, nil),
+			bloomTrieIndexer: light.NewBloomTrieIndexer(eth.ChainDb(), false, nil),
+			protocolManager:  pm,
+		},
+		quitSync:  quitSync,
+		lesTopics: lesTopics,
 	}
+
 	logger := log.New()
 
 	chtV1SectionCount, _, _ := srv.chtIndexer.Sections() // indexer still uses LES/1 4k section size for backwards server compatibility
@@ -104,7 +106,7 @@ func NewLesServer(eth *eth.Ethereum, config *eth.Config) (*LesServer, error) {
 }
 
 func (s *LesServer) Protocols() []p2p.Protocol {
-	return s.protocolManager.SubProtocols
+	return s.makeProtocols(ServerProtocolVersions)
 }
 
 // Start starts the LES server
```
