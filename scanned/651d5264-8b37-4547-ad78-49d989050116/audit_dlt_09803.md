# [?] Fixed data race. (#4544)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2023-10-26
Source: https://github.com/harmony-one/harmony/commit/b1389dacc452688584199958b58544c688e62e17
Type: security-commit

## Details
Fixed data race. (#4544)

* Fixed data race.

* Additional error checking for InsertChain.

## Patch
### api/service/legacysync/epoch_syncing.go
```diff
@@ -199,8 +199,18 @@ func processWithPayload(payload [][]byte, bc core.BlockChain) error {
 		decoded = append(decoded, block)
 	}
 
-	_, err := bc.InsertChain(decoded, true)
-	return err
+	for _, block := range decoded {
+		_, err := bc.InsertChain([]*types.Block{block}, true)
+		switch {
+		case errors.Is(err, core.ErrKnownBlock):
+			continue
+		case err != nil:
+			return err
+		default:
+		}
+	}
+
+	return nil
 }
 
 // CreateSyncConfig creates SyncConfig for StateSync object.
```

### api/service/stagedstreamsync/beacon_helper.go
```diff
@@ -1,8 +1,10 @@
 package stagedstreamsync
 
 import (
+	"errors"
 	"time"
 
+	"github.com/harmony-one/harmony/core"
 	"github.com/harmony-one/harmony/core/types"
 	"github.com/harmony-one/harmony/internal/utils"
 	"github.com/rs/zerolog"
@@ -126,7 +128,8 @@ func (bh *beaconHelper) insertLastMileBlocks() (inserted int, bn uint64, err err
 		}
 		// TODO: Instruct the beacon helper to verify signatures. This may require some forks
 		//       in pub-sub message (add commit sigs in node.block.sync messages)
-		if _, err = bh.bc.InsertChain(types.Blocks{b}, true); err != nil {
+		_, err = bh.bc.InsertChain(types.Blocks{b}, true)
+		if err != nil && !errors.Is(err, core.ErrKnownBlock) {
 			bn--
 			return
 		}
```

### api/service/stagedstreamsync/sig_verify.go
```diff
@@ -3,6 +3,7 @@ package stagedstreamsync
 import (
 	"fmt"
 
+	"github.com/harmony-one/harmony/core"
 	"github.com/harmony-one/harmony/core/types"
 	"github.com/harmony-one/harmony/crypto/bls"
 	"github.com/harmony-one/harmony/internal/chain"
@@ -53,8 +54,14 @@ func verifyAndInsertBlock(bc blockChain, block *types.Block, nextBlocks ...*type
 	if err := bc.Engine().VerifyHeader(bc, block.Header(), true); err != nil {
 		return errors.Wrap(err, "[VerifyHeader]")
 	}
-	if _, err := bc.InsertChain(types.Blocks{block}, false); err != nil {
+	_, err = bc.InsertChain(types.Blocks{block}, false)
+	switch {
+	case errors.Is(err, core.ErrKnownBlock):
+		return nil
+	case err != nil:
 		return errors.Wrap(err, "[InsertChain]")
+	default:
+
 	}
 	return nil
 }
```

### api/service/stagedstreamsync/stage_epoch.go
```diff
@@ -4,6 +4,7 @@ import (
 	"context"
 
 	"github.com/harmony-one/harmony/core"
+	"github.com/harmony-one/harmony/core/types"
 	"github.com/harmony-one/harmony/internal/utils"
 	sttypes "github.com/harmony-one/harmony/p2p/stream/types"
 	"github.com/harmony-one/harmony/shard"
@@ -129,13 +130,20 @@ func (sr *StageEpoch) doShortRangeSyncForEpochSync(ctx context.Context, s *Stage
 		return 0, nil
 	}
 
-	n, err := s.state.bc.InsertChain(blocks, true)
-	numBlocksInsertedShortRangeHistogramVec.With(s.state.promLabels()).Observe(float64(n))
-	if err != nil {
-		utils.Logger().Info().Err(err).Int("blocks inserted", n).Msg("Insert block failed")
-		sh.streamsFailed([]sttypes.StreamID{streamID}, "corrupted data")
-		return n, err
+	n := 0
+	for _, block := range blocks {
+		_, err := s.state.bc.InsertChain([]*types.Block{block}, true)
+		switch {
+		case errors.Is(err, core.ErrKnownBlock):
+		case err != nil:
+			utils.Logger().Info().Err(err).Int("blocks inserted", n).Msg("Insert block failed")
+			sh.streamsFailed([]sttypes.StreamID{streamID}, "corrupted data")
+			return n, err
+		default:
+		}
+		n++
 	}
+	numBlocksInsertedShortRangeHistogramVec.With(s.state.promLabels()).Observe(float64(n))
 	return n, nil
 }
 
```

### api/service/stagedstreamsync/staged_stream_sync.go
```diff
@@ -636,7 +636,8 @@ func (ss *StagedStreamSync) addConsensusLastMile(bc core.BlockChain, cs *consens
 			if block == nil {
 				break
 			}
-			if _, err := bc.InsertChain(types.Blocks{block}, true); err != nil {
+			_, err := bc.InsertChain(types.Blocks{block}, true)
+			if err != nil && !errors.Is(err, core.ErrKnownBlock) {
 				return errors.Wrap(err, "failed to InsertChain")
 			}
 			hashes = append(hashes, block.Header().Hash())
@@ -704,13 +705,16 @@ func (ss *StagedStreamSync) UpdateBlockAndStatus(block *types.Block, bc core.Blo
 	}
 
 	_, err := bc.InsertChain([]*types.Block{block}, false /* verifyHeaders */)
-	if err != nil {
+	switch {
+	case errors.Is(err, core.ErrKnownBlock):
+	case err != nil:
 		utils.Logger().Error().
 			Err(err).
 			Uint64("block number", block.NumberU64()).
 			Uint32("shard", block.ShardID()).
 			Msgf("[STAGED_STREAM_SYNC] UpdateBlockAndStatus: Error adding new block to blockchain")
 		return err
+	default:
 	}
 	utils.Logger().Info().
 		Uint64("blockHeight", block.NumberU64()).
```

### api/service/stagedsync/stage_state.go
```diff
@@ -178,7 +178,7 @@ func (stg *StageStates) Exec(firstCycle bool, invalidBlockRevert bool, s *StageS
 		headBeforeNewBlocks := stg.configs.bc.CurrentBlock().NumberU64()
 		headHashBeforeNewBlocks := stg.configs.bc.CurrentBlock().Hash()
 		_, err = stg.configs.bc.InsertChain(newBlocks, false) //TODO: verifyHeaders can be done here
-		if err != nil {
+		if err != nil && !errors.Is(err, core.ErrKnownBlock) {
 			// TODO: handle chain rollback because of bad block
 			utils.Logger().Error().
 				Err(err).
```

### api/service/stagedsync/stagedsync.go
```diff
@@ -1091,13 +1091,16 @@ func (ss *StagedSync) UpdateBlockAndStatus(block *types.Block, bc core.BlockChai
 	}
 
 	_, err := bc.InsertChain([]*types.Block{block}, false /* verifyHeaders */)
-	if err != nil {
+	switch {
+	case errors.Is(err, core.ErrKnownBlock):
+	case err != nil:
 		utils.Logger().Error().
 			Err(err).
 			Uint64("block number", block.NumberU64()).
 			Uint32("shard", block.ShardID()).
 			Msgf("[STAGED_SYNC] UpdateBlockAndStatus: Error adding new block to blockchain")
 		return err
+	default:
 	}
 	utils.Logger().Info().
 		Uint64("blockHeight", block.NumberU64()).
@@ -1218,7 +1221,7 @@ func (ss *StagedSync) addConsensusLastMile(bc core.BlockChain, cs *consensus.Con
 			if block == nil {
 				break
 			}
-			if _, err := bc.InsertChain(types.Blocks{block}, true); err != nil {
+			if _, err := bc.InsertChain(types.Blocks{block}, true); err != nil && !errors.Is(err, core.ErrKnownBlock) {
 				return errors.Wrap(err, "failed to InsertChain")
 			}
 		}
```

### consensus/consensus_v2.go
```diff
@@ -661,7 +661,8 @@ func (consensus *Consensus) tryCatchup() error {
 
 func (consensus *Consensus) commitBlock(blk *types.Block, committedMsg *FBFTMessage) error {
 	if consensus.Blockchain().CurrentBlock().NumberU64() < blk.NumberU64() {
-		if _, err := consensus.Blockchain().InsertChain([]*types.Block{blk}, !consensus.fBFTLog.IsBlockVerified(blk.Hash())); err != nil {
+		_, err := consensus.Blockchain().InsertChain([]*types.Block{blk}, !consensus.fBFTLog.IsBlockVerified(blk.Hash()))
+		if err != nil && !errors.Is(err, core.ErrKnownBlock) {
 			consensus.getLogger().Error().Err(err).Msg("[commitBlock] Failed to add block to chain")
 			return err
 		}
```

### consensus/downloader.go
```diff
@@ -2,6 +2,7 @@ package consensus
 
 import (
 	"github.com/ethereum/go-ethereum/event"
+	"github.com/harmony-one/harmony/core"
 	"github.com/harmony-one/harmony/core/types"
 	"github.com/pkg/errors"
 )
@@ -93,7 +94,7 @@ func (consensus *Consensus) AddConsensusLastMile() error {
 			if block == nil {
 				break
 			}
-			if _, err := consensus.Blockchain().InsertChain(types.Blocks{block}, true); err != nil {
+			if _, err := consensus.Blockchain().InsertChain(types.Blocks{block}, true); err != nil && !errors.Is(err, core.ErrKnownBlock) {
 				return errors.Wrap(err, "failed to InsertChain")
 			}
 		}
```

### node/node_explorer.go
```diff
@@ -154,7 +154,7 @@ func (node *Node) AddNewBlockForExplorer(block *types.Block) {
 
 	utils.Logger().Info().Uint64("blockHeight", block.NumberU64()).Msg("[Explorer] Adding new block for explorer node")
 
-	if _, err := node.Blockchain().InsertChain([]*types.Block{block}, false); err == nil {
+	if _, err := node.Blockchain().InsertChain([]*types.Block{block}, false); err == nil || errors.Is(err, core.ErrKnownBlock) {
 		if block.IsLastBlockInEpoch() {
 			node.Consensus.UpdateConsensusInformation()
 		}
```

### p2p/host.go
```diff
@@ -254,7 +254,7 @@ func NewHost(cfg HostConfig) (Host, error) {
 	self.PeerID = p2pHost.ID()
 	subLogger := utils.Logger().With().Str("hostID", p2pHost.ID().Pretty()).Logger()
 
-	security := security.NewManager(cfg.MaxConnPerIP, cfg.MaxPeers)
+	security := security.NewManager(cfg.MaxConnPerIP, int(cfg.MaxPeers))
 	// has to save the private key for host
 	h := &HostV2{
 		h:             p2pHost,
```

### p2p/security/security.go
```diff
@@ -3,7 +3,6 @@ package security
 import (
 	"fmt"
 	"sync"
-	"sync/atomic"
 
 	"github.com/harmony-one/harmony/internal/utils"
 	libp2p_network "github.com/libp2p/go-libp2p/core/network"
@@ -18,56 +17,53 @@ type Security interface {
 
 type Manager struct {
 	maxConnPerIP int
-	maxPeers     int64
+	maxPeers     int
 
 	mutex sync.Mutex
-	peers peerMap // All the connected nodes, key is the Peer's IP, value is the peer's ID array
+	peers *peerMap // All the connected nodes, key is the Peer's IP, value is the peer's ID array
 }
 
 type peerMap struct {
-	count int64
-	peers sync.Map
+	peers map[string][]string
 }
 
-func (peerMap *peerMap) Len() int64 {
-	return atomic.LoadInt64(&peerMap.count)
+func newPeersMap() *peerMap {
+	return &peerMap{
+		peers: make(map[string][]string),
+	}
 }
 
-func (peerMap *peerMap) Store(key, value interface{}) {
-	// only increment if you didn't have this key
-	hasKey := peerMap.HasKey(key)
-	peerMap.peers.Store(key, value)
-	if !hasKey {
-		atomic.AddInt64(&peerMap.count, 1)
-	}
+func (peerMap *peerMap) Len() int {
+	return len(peerMap.peers)
 }
 
-func (peerMap *peerMap) HasKey(key interface{}) bool {
-	hasKey := false
-	peerMap.peers.Range(func(k, v interface{}) bool {
-		if k == key {
-			hasKey = true
-			return false
-		}
-		return true
-	})
-	return hasKey
+func (peerMap *peerMap) Store(key string, value []string) {
+	peerMap.peers[key] = value
+}
+
+func (peerMap *peerMap) HasKey(key string) bool {
+	_, ok := peerMap.peers[key]
+	return ok
 }
 
-func (peerMap *peerMap) Delete(key interface{}) {
-	peerMap.peers.Delete(key)
-	atomic.AddInt64(&peerMap.count, -1)
+func (peerMap *peerMap) Delete(key string) {
+	delete(peerMap.peers, key)
 }
 
-func (peerMap *peerMap) Load(key interface{}) (value interface{}, ok bool) {
-	return peerMap.peers.Load(key)
+func (peerMap *peerMap) Load(key string) (value []string, ok bool) {
+	value, ok = peerMap.peers[key]
+	return value, ok
 }
 
-func (peerMap *peerMap) Range(f func(key, value any) bool) {
-	peerMap.peers.Range(f)
+func (peerMap *peerMap) Range(f func(key string, value []string) bool) {
+	for key, value := range peerMap.peers {
+		if !f(key, value) {
+			break
+		}
+	}
 }
 
-func NewManager(maxConnPerIP int, maxPeers int64) *Manager {
+func NewManager(maxConnPerIP int, maxPeers int) *Manager {
 	if maxConnPerIP < 0 {
 		panic("maximum connections per IP must not be negative")
 	}
@@ -77,9 +73,16 @@ func NewManager(maxConnPerIP int, maxPeers int64) *Manager {
 	return &Manager{
 		maxConnPerIP: maxConnPerIP,
 		maxPeers:     maxPeers,
+		peers:        newPeersMap(),
 	}
 }
 
+func (m *Manager) RangePeers(f func(key string, value []string) bool) {
+	m.mutex.Lock()
+	defer m.mutex.Unlock()
+	m.peers.Range(f)
+}
+
 func (m *Manager) OnConnectCheck(net libp2p_network.Network, conn libp2p_network.Conn) error {
 	m.mutex.Lock()
 	defer m.mutex.Unlock()
@@ -89,19 +92,11 @@ func (m *Manager) OnConnectCheck(net libp2p_network.Network, conn libp2p_network
 		return errors.Wrap(err, "failed on get remote ip")
 	}
 
-	value, ok := m.peers.Load(remoteIp)
-	if !ok {
-		value = []string{}
-	}
-
-	peers, ok := value.([]string)
-	if !ok {
-		return errors.New("peers info type err")
-	}
+	peers, _ := m.peers.Load(remoteIp)
 
 	// avoid add repeatedly
 	peerID := conn.RemotePeer().String()
-	_, ok = find(peers, peerID)
+	_, ok := find(peers, peerID)
 	if !ok {
 		peers = append(peers, peerID)
 	}
@@ -118,7 +113,7 @@ func (m *Manager) OnConnectCheck(net libp2p_network.Network, conn libp2p_network
 	// only limit addition if it's a new peer and not an existing peer with new connection
 	if m.maxPeers > 0 && currentPeerCount >= m.maxPeers && !m.peers.HasKey(remoteIp) {
 		utils.Logger().Warn().
-			Int64("connected peers", currentPeerCount).
+			Int("connected peers", currentPeerCount).
 			Str("new peer", remoteIp).
 			Msg("too many peers, closing")
 		return net.ClosePeer(conn.RemotePeer())
@@ -136,16 +131,11 @@ func (m *Manager) OnDisconnectCheck(conn libp2p_network.Conn) error {
 		return errors.Wrap(err, "failed on get ip")
 	}
 
-	value, ok := m.peers.Load(ip)
+	peers, ok := m.peers.Load(ip)
 	if !ok {
 		return nil
 	}
 
-	peers, ok := value.([]string)
-	if !ok {
-		return errors.New("peers info type err")
-	}
-
 	peerID := conn.RemotePeer().String()
 	index, ok := find(peers, peerID)
 	if ok {
```
