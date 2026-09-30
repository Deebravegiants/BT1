# [?] Fix data race issue in caplin unittest  (#17020)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-09-12
Source: https://github.com/erigontech/erigon/commit/11b751442a82ca1e8cebd9dfd486cf2faf8e6755
Type: security-commit

## Details
Fix data race issue in caplin unittest  (#17020)

fix unittest
https://github.com/erigontech/erigon/issues/15001
https://github.com/erigontech/erigon/issues/14997

## Patch
### cl/phase1/network/services/batch_signature_verification.go
```diff
@@ -14,10 +14,10 @@ import (
 const (
 	batchSignatureVerificationThreshold = 50
 	reservedSize                        = 512
+	batchCheckInterval                  = 500 * time.Millisecond
 )
 
 var (
-	batchCheckInterval          = 500 * time.Millisecond
 	blsVerifyMultipleSignatures = bls.VerifyMultipleSignatures
 )
 
```

### cl/phase1/network/services/voluntary_exit_service_test.go
```diff
@@ -20,7 +20,6 @@ import (
 	"context"
 	"log"
 	"testing"
-	"time"
 
 	"github.com/erigontech/erigon-lib/types/ssz"
 	"github.com/erigontech/erigon/cl/antiquary/tests"
@@ -63,8 +62,7 @@ func (t *voluntaryExitTestSuite) SetupTest() {
 	t.ethClock = eth_clock.NewMockEthereumClock(t.gomockCtrl)
 	t.beaconCfg = &clparams.BeaconChainConfig{}
 	batchSignatureVerifier := NewBatchSignatureVerifier(context.TODO(), nil)
-	batchCheckInterval = 1 * time.Millisecond
-	go batchSignatureVerifier.Start()
+	batchSignatureVerifier.Start()
 	t.voluntaryExitService = NewVoluntaryExitService(*t.operationsPool, t.emitters, t.syncedData, t.beaconCfg, t.ethClock, batchSignatureVerifier)
 	// mock global functions
 	t.mockFuncs = &mockFuncs{
@@ -252,6 +250,6 @@ func (t *voluntaryExitTestSuite) TestProcessMessage() {
 }
 
 func TestVoluntaryExit(t *testing.T) {
-	t.Skip("issue #14997")
+	//t.Skip("issue #14997")
 	suite.Run(t, new(voluntaryExitTestSuite))
 }
```

### cl/sentinel/sentinel.go
```diff
@@ -288,6 +288,8 @@ func (s *Sentinel) observeBandwidth(ctx context.Context) {
 			}
 			s.GossipManager().subscriptions.Range(func(key, value any) bool {
 				sub := value.(*GossipSubscription)
+				sub.lock.Lock()
+				defer sub.lock.Unlock()
 				if sub.topic == nil {
 					return true
 				}
```

### cl/sentinel/sentinel_gossip_test.go
```diff
@@ -19,13 +19,15 @@ package sentinel
 import (
 	"context"
 	"math"
+	"sync/atomic"
 	"testing"
 	"time"
 
 	"github.com/libp2p/go-libp2p/core/peer"
 	"github.com/stretchr/testify/require"
 	gomock "go.uber.org/mock/gomock"
 
+	"github.com/erigontech/erigon-lib/common"
 	"github.com/erigontech/erigon-lib/log/v3"
 	"github.com/erigontech/erigon/cl/clparams"
 	"github.com/erigontech/erigon/cl/clparams/initial_state"
@@ -42,28 +44,49 @@ func getEthClock(t *testing.T) eth_clock.EthereumClock {
 }
 
 func TestSentinelGossipOnHardFork(t *testing.T) {
-	t.Skip("issue #15001")
+	//t.Skip("issue #15001")
 
 	listenAddrHost := "127.0.0.1"
 
 	ctx := context.Background()
 	db, _, _, _, _, reader := loadChain(t)
 	networkConfig, beaconConfig := clparams.GetConfigsByNetwork(chainspec.MainnetChainID)
 	bcfg := *beaconConfig
-
-	s, err := initial_state.GetGenesisState(chainspec.MainnetChainID)
-	require.NoError(t, err)
-	ethClock := eth_clock.NewEthereumClock(s.GenesisTime(), s.GenesisValidatorsRoot(), &bcfg)
-
-	bcfg.AltairForkEpoch = math.MaxUint64
-	bcfg.BellatrixForkEpoch = math.MaxUint64
-	bcfg.CapellaForkEpoch = math.MaxUint64
-	bcfg.DenebForkEpoch = math.MaxUint64
-	bcfg.ElectraForkEpoch = math.MaxUint64
 	bcfg.InitializeForkSchedule()
 
-	// Create mock PeerDasStateReader
+	// mock eth clock
 	ctrl := gomock.NewController(t)
+	ethClock := eth_clock.NewMockEthereumClock(ctrl)
+	var hardFork atomic.Bool
+	hardFork.Store(false)
+	ethClock.EXPECT().CurrentForkDigest().DoAndReturn(func() (common.Bytes4, error) {
+		if hardFork.Load() {
+			forkDigest := common.Bytes4{0x00, 0x00, 0x00, 0x01}
+			return forkDigest, nil
+		}
+		return common.Bytes4{0x00, 0x00, 0x00, 0x00}, nil
+	}).AnyTimes()
+	ethClock.EXPECT().ForkId().DoAndReturn(func() ([]byte, error) {
+		if hardFork.Load() {
+			return []byte{0x00, 0x00, 0x00, 0x01}, nil
+		}
+		return []byte{0x00, 0x00, 0x00, 0x00}, nil
+	}).AnyTimes()
+	ethClock.EXPECT().NextForkDigest().DoAndReturn(func() (common.Bytes4, error) {
+		if hardFork.Load() {
+			return common.Bytes4{0x00, 0x00, 0x00, 0x02}, nil
+		}
+		return common.Bytes4{0x00, 0x00, 0x00, 0x01}, nil
+	}).AnyTimes()
+	ethClock.EXPECT().GetCurrentEpoch().DoAndReturn(func() uint64 {
+		if hardFork.Load() {
+			return uint64(1)
+		}
+		return uint64(0)
+	}).AnyTimes()
+	ethClock.EXPECT().NextForkEpochIncludeBPO().Return(bcfg.FarFutureEpoch).AnyTimes()
+
+	// Create mock PeerDasStateReader
 	mockPeerDasStateReader := peerdasstatemock.NewMockPeerDasStateReader(ctrl)
 	mockPeerDasStateReader.EXPECT().GetEarliestAvailableSlot().Return(uint64(0)).AnyTimes()
 	mockPeerDasStateReader.EXPECT().GetRealCgc().Return(uint64(0)).AnyTimes()
@@ -122,15 +145,14 @@ func TestSentinelGossipOnHardFork(t *testing.T) {
 		// delay to make sure that the connection is established
 		sub1.Publish(msg)
 	}()
-	var previousTopic string
 
 	ans := <-ch
 	require.Equal(t, ans.Data, msg)
-	previousTopic = ans.TopicName
 
-	bcfg.AltairForkEpoch = clparams.MainnetBeaconConfig.AltairForkEpoch
-	bcfg.InitializeForkSchedule()
-	time.Sleep(5 * time.Second)
+	// check if it still works after hard fork
+	previousTopic := ans.TopicName
+	hardFork.Store(true)
+	time.Sleep(1 * time.Second)
 
 	msg = []byte("hello1")
 	go func() {
@@ -142,5 +164,4 @@ func TestSentinelGossipOnHardFork(t *testing.T) {
 	ans = <-ch
 	require.Equal(t, ans.Data, msg)
 	require.NotEqual(t, previousTopic, ans.TopicName)
-
 }
```
