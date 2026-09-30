# [?] Fixed panic with dsync. (#4562)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2023-11-16
Source: https://github.com/harmony-one/harmony/commit/582a4cf5cb27b3c87210035c4200d42258c9ffdf
Type: security-commit

## Details
Fixed panic with dsync. (#4562)

## Patch
### cmd/harmony/main.go
```diff
@@ -862,7 +862,7 @@ func setupConsensusAndNode(hc harmonyconfig.HarmonyConfig, nodeConfig *nodeconfi
 	currentNode.NodeConfig.ConsensusPriKey = nodeConfig.ConsensusPriKey
 
 	// This needs to be executed after consensus setup
-	if err := currentNode.InitConsensusWithValidators(); err != nil {
+	if err := currentConsensus.InitConsensusWithValidators(); err != nil {
 		utils.Logger().Warn().
 			Int("shardID", hc.General.ShardID).
 			Err(err).
```

### consensus/consensus.go
```diff
@@ -6,19 +6,20 @@ import (
 	"sync/atomic"
 	"time"
 
-	"github.com/harmony-one/harmony/consensus/engine"
-	"github.com/harmony-one/harmony/core"
-	"github.com/harmony-one/harmony/crypto/bls"
-	"github.com/harmony-one/harmony/internal/registry"
-
 	"github.com/harmony-one/abool"
 	bls_core "github.com/harmony-one/bls/ffi/go/bls"
+	"github.com/harmony-one/harmony/consensus/engine"
 	"github.com/harmony-one/harmony/consensus/quorum"
+	"github.com/harmony-one/harmony/core"
 	"github.com/harmony-one/harmony/core/types"
+	"github.com/harmony-one/harmony/crypto/bls"
 	bls_cosi "github.com/harmony-one/harmony/crypto/bls"
+	"github.com/harmony-one/harmony/internal/registry"
 	"github.com/harmony-one/harmony/internal/utils"
 	"github.com/harmony-one/harmony/multibls"
 	"github.com/harmony-one/harmony/p2p"
+	"github.com/harmony-one/harmony/shard"
+	"github.com/harmony-one/harmony/shard/committee"
 	"github.com/harmony-one/harmony/staking/slash"
 	"github.com/pkg/errors"
 )
@@ -121,7 +122,9 @@ type Consensus struct {
 	// finalityCounter keep tracks of the finality time
 	finalityCounter atomic.Value //int64
 
-	dHelper *downloadHelper
+	dHelper interface {
+		DownloadAsync()
+	}
 
 	// Both flags only for initialization state.
 	start           bool
@@ -177,6 +180,10 @@ func (consensus *Consensus) verifyBlock(block *types.Block) error {
 // BlocksSynchronized lets the main loop know that block synchronization finished
 // thus the blockchain is likely to be up to date.
 func (consensus *Consensus) BlocksSynchronized() {
+	err := consensus.AddConsensusLastMile()
+	if err != nil {
+		consensus.GetLogger().Error().Err(err).Msg("add last mile failed")
+	}
 	consensus.mutex.Lock()
 	defer consensus.mutex.Unlock()
 	consensus.syncReadyChan()
@@ -274,6 +281,7 @@ func New(
 		msgSender:    NewMessageSender(host),
 		// FBFT timeout
 		consensusTimeout: createTimeout(),
+		dHelper:          downloadAsync{},
 	}
 
 	if multiBLSPriKey != nil {
@@ -311,3 +319,68 @@ func (consensus *Consensus) GetHost() p2p.Host {
 func (consensus *Consensus) Registry() *registry.Registry {
 	return consensus.registry
 }
+
+// InitConsensusWithValidators initialize shard state
+// from latest epoch and update committee pub
+// keys for consensus
+func (consensus *Consensus) InitConsensusWithValidators() (err error) {
+	shardID := consensus.ShardID
+	currentBlock := consensus.Blockchain().CurrentBlock()
+	blockNum := currentBlock.NumberU64()
+	consensus.SetMode(Listening)
+	epoch := currentBlock.Epoch()
+	utils.Logger().Info().
+		Uint64("blockNum", blockNum).
+		Uint32("shardID", shardID).
+		Uint64("epoch", epoch.Uint64()).
+		Msg("[InitConsensusWithValidators] Try To Get PublicKeys")
+	shardState, err := committee.WithStakingEnabled.Compute(
+		epoch, consensus.Blockchain(),
+	)
+	if err != nil {
+		utils.Logger().Err(err).
+			Uint64("blockNum", blockNum).
+			Uint32("shardID", shardID).
+			Uint64("epoch", epoch.Uint64()).
+			Msg("[InitConsensusWithValidators] Failed getting shard state")
+		return err
+	}
+	subComm, err := shardState.FindCommitteeByID(shardID)
+	if err != nil {
+		utils.Logger().Err(err).
+			Interface("shardState", shardState).
+			Msg("[InitConsensusWithValidators] Find CommitteeByID")
+		return err
+	}
+	pubKeys, err := subComm.BLSPublicKeys()
+	if err != nil {
+		utils.Logger().Error().
+			Uint32("shardID", shardID).
+			Uint64("blockNum", blockNum).
+			Msg("[InitConsensusWithValidators] PublicKeys is Empty, Cannot update public keys")
+		return errors.Wrapf(
+			err,
+			"[InitConsensusWithValidators] PublicKeys is Empty, Cannot update public keys",
+		)
+	}
+
+	for _, key := range pubKeys {
+		if consensus.GetPublicKeys().Contains(key.Object) {
+			utils.Logger().Info().
+				Uint64("blockNum", blockNum).
+				Int("numPubKeys", len(pubKeys)).
+				Str("mode", consensus.Mode().String()).
+				Msg("[InitConsensusWithValidators] Successfully updated public keys")
+			consensus.UpdatePublicKeys(pubKeys, shard.Schedule.InstanceForEpoch(epoch).ExternalAllowlist())
+			consensus.SetMode(Normal)
+			return nil
+		}
+	}
+	return nil
+}
+
+type downloadAsync struct {
+}
+
+func (a downloadAsync) DownloadAsync() {
+}
```

### consensus/consensus_v2.go
```diff
@@ -277,6 +277,8 @@ func (consensus *Consensus) BlockCommitSigs(blockNum uint64) ([]byte, error) {
 		return nil, nil
 	}
 	lastCommits, err := consensus.Blockchain().ReadCommitSig(blockNum)
+	consensus.mutex.Lock()
+	defer consensus.mutex.Unlock()
 	if err != nil ||
 		len(lastCommits) < bls.BLSSignatureSizeInBytes {
 		msgs := consensus.FBFTLog().GetMessagesByTypeSeq(
@@ -300,30 +302,26 @@ func (consensus *Consensus) BlockCommitSigs(blockNum uint64) ([]byte, error) {
 func (consensus *Consensus) Start(
 	stopChan chan struct{},
 ) {
+	consensus.GetLogger().Info().Time("time", time.Now()).Msg("[ConsensusMainLoop] Consensus started")
 	go func() {
-		consensus.getLogger().Info().Time("time", time.Now()).Msg("[ConsensusMainLoop] Consensus started")
-		go func() {
-			ticker := time.NewTicker(250 * time.Millisecond)
-			defer ticker.Stop()
-			for {
-				select {
-				case <-stopChan:
-					return
-				case <-ticker.C:
-					consensus.Tick()
-				}
+		ticker := time.NewTicker(250 * time.Millisecond)
+		defer ticker.Stop()
+		for {
+			select {
+			case <-stopChan:
+				return
+			case <-ticker.C:
+				consensus.Tick()
 			}
-		}()
-
-		consensus.mutex.Lock()
-		consensus.consensusTimeout[timeoutBootstrap].Start()
-		consensus.getLogger().Info().Msg("[ConsensusMainLoop] Start bootstrap timeout (only once)")
-		// Set up next block due time.
-		consensus.NextBlockDue = time.Now().Add(consensus.BlockPeriod)
-		consensus.mutex.Unlock()
+		}
 	}()
 
-	consensus.dHelper.start()
+	consensus.mutex.Lock()
+	consensus.consensusTimeout[timeoutBootstrap].Start()
+	consensus.getLogger().Info().Msg("[ConsensusMainLoop] Start bootstrap timeout (only once)")
+	// Set up next block due time.
+	consensus.NextBlockDue = time.Now().Add(consensus.BlockPeriod)
+	consensus.mutex.Unlock()
 }
 
 func (consensus *Consensus) StartChannel() {
```

### consensus/downloader.go
```diff
@@ -19,12 +19,13 @@ type downloader interface {
 // Set downloader set the downloader of the shard to consensus
 // TODO: It will be better to move this to consensus.New and register consensus as a service
 func (consensus *Consensus) SetDownloader(d downloader) {
+	consensus.mutex.Lock()
+	defer consensus.mutex.Unlock()
 	consensus.dHelper = newDownloadHelper(consensus, d)
 }
 
 type downloadHelper struct {
 	d downloader
-	c *Consensus
 
 	startedCh  chan struct{}
 	finishedCh chan struct{}
@@ -41,46 +42,42 @@ func newDownloadHelper(c *Consensus, d downloader) *downloadHelper {
 	finishedSub := d.SubscribeDownloadFinished(finishedCh)
 
 	out := &downloadHelper{
-		c:           c,
 		d:           d,
 		startedCh:   startedCh,
 		finishedCh:  finishedCh,
 		startedSub:  startedSub,
 		finishedSub: finishedSub,
 	}
-	go out.downloadStartedLoop()
-	go out.downloadFinishedLoop()
+	go out.downloadStartedLoop(c)
+	go out.downloadFinishedLoop(c)
 	return out
 }
 
-func (dh *downloadHelper) start() {
+func (dh *downloadHelper) DownloadAsync() {
+	dh.d.DownloadAsync()
 }
 
-func (dh *downloadHelper) downloadStartedLoop() {
+func (dh *downloadHelper) downloadStartedLoop(c *Consensus) {
 	for {
 		select {
 		case <-dh.startedCh:
-			dh.c.BlocksNotSynchronized()
+			c.BlocksNotSynchronized()
 
 		case err := <-dh.startedSub.Err():
-			dh.c.getLogger().Info().Err(err).Msg("consensus download finished loop closed")
+			c.GetLogger().Info().Err(err).Msg("consensus download finished loop closed")
 			return
 		}
 	}
 }
 
-func (dh *downloadHelper) downloadFinishedLoop() {
+func (dh *downloadHelper) downloadFinishedLoop(c *Consensus) {
 	for {
 		select {
 		case <-dh.finishedCh:
-			err := dh.c.AddConsensusLastMile()
-			if err != nil {
-				dh.c.getLogger().Error().Err(err).Msg("add last mile failed")
-			}
-			dh.c.BlocksSynchronized()
+			c.BlocksSynchronized()
 
 		case err := <-dh.finishedSub.Err():
-			dh.c.getLogger().Info().Err(err).Msg("consensus download finished loop closed")
+			c.GetLogger().Info().Err(err).Msg("consensus download finished loop closed")
 			return
 		}
 	}
@@ -104,7 +101,7 @@ func (consensus *Consensus) AddConsensusLastMile() error {
 }
 
 func (consensus *Consensus) spinUpStateSync() {
-	consensus.dHelper.d.DownloadAsync()
+	consensus.dHelper.DownloadAsync()
 	consensus.current.SetMode(Syncing)
 	for _, v := range consensus.consensusTimeout {
 		v.Stop()
```

### node/node.go
```diff
@@ -52,7 +52,6 @@ import (
 	"github.com/harmony-one/harmony/node/worker"
 	"github.com/harmony-one/harmony/p2p"
 	"github.com/harmony-one/harmony/shard"
-	"github.com/harmony-one/harmony/shard/committee"
 	"github.com/harmony-one/harmony/staking/reward"
 	"github.com/harmony-one/harmony/staking/slash"
 	staking "github.com/harmony-one/harmony/staking/types"
@@ -1196,72 +1195,6 @@ func (node *Node) updateInitialRewardValues() {
 	reward.SetTotalInitialTokens(initTotal)
 }
 
-// InitConsensusWithValidators initialize shard state
-// from latest epoch and update committee pub
-// keys for consensus
-func (node *Node) InitConsensusWithValidators() (err error) {
-	if node.Consensus == nil {
-		utils.Logger().Error().
-			Msg("[InitConsensusWithValidators] consenus is nil; Cannot figure out shardID")
-		return errors.New(
-			"[InitConsensusWithValidators] consenus is nil; Cannot figure out shardID",
-		)
-	}
-	shardID := node.Consensus.ShardID
-	currentBlock := node.Blockchain().CurrentBlock()
-	blockNum := currentBlock.NumberU64()
-	node.Consensus.SetMode(consensus.Listening)
-	epoch := currentBlock.Epoch()
-	utils.Logger().Info().
-		Uint64("blockNum", blockNum).
-		Uint32("shardID", shardID).
-		Uint64("epoch", epoch.Uint64()).
-		Msg("[InitConsensusWithValidators] Try To Get PublicKeys")
-	shardState, err := committee.WithStakingEnabled.Compute(
-		epoch, node.Consensus.Blockchain(),
-	)
-	if err != nil {
-		utils.Logger().Err(err).
-			Uint64("blockNum", blockNum).
-			Uint32("shardID", shardID).
-			Uint64("epoch", epoch.Uint64()).
-			Msg("[InitConsensusWithValidators] Failed getting shard state")
-		return err
-	}
-	subComm, err := shardState.FindCommitteeByID(shardID)
-	if err != nil {
-		utils.Logger().Err(err).
-			Interface("shardState", shardState).
-			Msg("[InitConsensusWithValidators] Find CommitteeByID")
-		return err
-	}
-	pubKeys, err := subComm.BLSPublicKeys()
-	if err != nil {
-		utils.Logger().Error().
-			Uint32("shardID", shardID).
-			Uint64("blockNum", blockNum).
-			Msg("[InitConsensusWithValidators] PublicKeys is Empty, Cannot update public keys")
-		return errors.Wrapf(
-			err,
-			"[InitConsensusWithValidators] PublicKeys is Empty, Cannot update public keys",
-		)
-	}
-
-	for _, key := range pubKeys {
-		if node.Consensus.GetPublicKeys().Contains(key.Object) {
-			utils.Logger().Info().
-				Uint64("blockNum", blockNum).
-				Int("numPubKeys", len(pubKeys)).
-				Str("mode", node.Consensus.Mode().String()).
-				Msg("[InitConsensusWithValidators] Successfully updated public keys")
-			node.Consensus.UpdatePublicKeys(pubKeys, shard.Schedule.InstanceForEpoch(epoch).ExternalAllowlist())
-			node.Consensus.SetMode(consensus.Normal)
-			return nil
-		}
-	}
-	return nil
-}
-
 func (node *Node) initNodeConfiguration() (service.NodeConfig, chan p2p.Peer, error) {
 	chanPeer := make(chan p2p.Peer)
 	nodeConfig := service.NodeConfig{
```
