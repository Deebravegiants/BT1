# [?] Fix the race condition in local_rolldpos_test.go when rpc server starts later than conesensus

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2018-06-09
Source: https://github.com/iotexproject/iotex-core/commit/02a6956957c210f0eebd7411068147a71b1b423d
Type: security-commit

## Details
Fix the race condition in local_rolldpos_test.go when rpc server starts later than conesensus

## Patch
### blocksync/blocksync.go
```diff
@@ -365,7 +365,10 @@ func (bs *blockSyncer) commitBlocksInBuffer() error {
 		bs.tp.RemoveTxInBlock(blk)
 
 		//TODO make it structured logging
-		logger.Warn().Msgf("------ commit block %d time = %v\n\n", next, time.Since(bs.actionTime))
+		logger.Warn().
+			Str("name", bs.p2p.PRC.String()).
+			Uint64("height", blk.Height()).
+			Msg("commit a block")
 		bs.actionTime = time.Now()
 
 		// update sliding window
```

### consensus/fsm/fsm.go
```diff
@@ -292,7 +292,7 @@ func (m *Machine) transitionTo(dest State) error {
 		return errors.Wrapf(ErrStateUndefined, "state %s has not been registered", dest)
 	}
 
-	logger.Debug().
+	logger.Info().
 		Str("name", m.name).
 		Str("src", string(m.state)).
 		Str("dst", string(dest)).
```

### e2etests/config_local_rolldpos.yaml
```diff
@@ -45,6 +45,7 @@ consensus:
             ttl: 90ms
         acceptvote:
             ttl: 90ms
+        delay: 2s
     blockcreationinterval: 1s
 
 blocksync:
```

### e2etests/local_rolldpos_test.go
```diff
@@ -45,6 +45,10 @@ func TestLocalRollDPoS(t *testing.T) {
 	t.Run("PseudoRotatedProposer-PseudoStarNewEpoch-NoInterval", func(t *testing.T) {
 		testLocalRollDPoS("PseudoRotatedProposer", "PseudoStarNewEpoch", 8, t, 0)
 	})
+	t.Run("PseudoRotatedProposer-PseudoStarNewEpoch-Interval", func(t *testing.T) {
+		testLocalRollDPoS(
+			"PseudoRotatedProposer", "PseudoStarNewEpoch", 8, t, 100*time.Millisecond)
+	})
 }
 
 // 4 delegates and 3 full nodes
@@ -88,7 +92,7 @@ func testLocalRollDPoS(prCb string, epochCb string, numBlocks uint64, t *testing
 		defer svr.Stop()
 	}
 
-	err = util.WaitUntil(time.Millisecond*200, time.Second*4, func() (bool, error) {
+	err = util.WaitUntil(time.Millisecond*200, time.Second*10, func() (bool, error) {
 		for _, svr := range svrs {
 			bc := svr.Bc()
 			if bc == nil {
```

### network/rpcserver.go
```diff
@@ -33,6 +33,8 @@ type RPCServer struct {
 	Overlay   *Overlay
 	counters  sync.Map
 	rateLimit uint64
+	// TODO: mutation of this field is not thread safe
+	started bool
 }
 
 // NewRPCServer creates an instance of RPCServer
@@ -145,16 +147,25 @@ func (s *RPCServer) Start() error {
 	// Register reflection service on gRPC peer.
 	reflection.Register(s.Server)
 	go func() {
+		logger.Info().Str("addr", s.String()).Msg("start PRC server")
+		s.started = true
 		if err := s.Server.Serve(lis); err != nil {
 			logger.Fatal().Err(err).Msg("Node failed to serve")
 		}
 	}()
 	return nil
 }
 
+// Started returns the boolean to indicate whether the rpc server is started
+func (s *RPCServer) Started() bool {
+	return s.started
+}
+
 // Stop stops the rpc server
 func (s *RPCServer) Stop() error {
+	logger.Info().Str("addr", s.String()).Msg("stop PRC server")
 	s.Server.Stop()
+	s.started = false
 	return nil
 }
 
```

### network/rpcserver_test.go
```diff
@@ -18,6 +18,7 @@ import (
 	pb "github.com/iotexproject/iotex-core/network/proto"
 	"github.com/iotexproject/iotex-core/proto"
 	"github.com/iotexproject/iotex-core/test/mock/mock_dispatcher"
+	"github.com/iotexproject/iotex-core/test/util"
 )
 
 func TestRpcPingPong(t *testing.T) {
@@ -35,6 +36,8 @@ func TestRpcPingPong(t *testing.T) {
 		s.Stop()
 	}()
 
+	util.WaitUntil(10*time.Millisecond, 2*time.Second, func() (bool, error) { return o.PRC.Started(), nil })
+
 	pong, err := p.Ping(&pb.Ping{Nonce: uint64(4689), Addr: "127.0.0.1:10001"})
 	assert.Nil(t, err)
 	assert.NotNil(t, pong)
@@ -62,6 +65,8 @@ func TestGetPeers(t *testing.T) {
 		s.Stop()
 	}()
 
+	util.WaitUntil(10*time.Millisecond, 2*time.Second, func() (bool, error) { return o.PRC.Started(), nil })
+
 	res, err := p.GetPeers(&pb.GetPeersReq{Count: 1})
 	assert.Nil(t, err)
 	assert.NotNil(t, res)
@@ -102,6 +107,8 @@ func TestBroadcast(t *testing.T) {
 		s.Stop()
 	}()
 
+	util.WaitUntil(10*time.Millisecond, 2*time.Second, func() (bool, error) { return o.PRC.Started(), nil })
+
 	txMsg := &iproto.TxPb{}
 	b, _ := proto.Marshal(txMsg)
 	res, err := p.BroadcastMsg(
@@ -130,6 +137,8 @@ func TestRPCTell(t *testing.T) {
 		mctrl.Finish()
 	}()
 
+	util.WaitUntil(10*time.Millisecond, 2*time.Second, func() (bool, error) { return o.PRC.Started(), nil })
+
 	txMsg := &iproto.TxPb{}
 	b, _ := proto.Marshal(txMsg)
 	res, err := p.Tell(&pb.TellReq{Header: iproto.MagicBroadcastMsgHeader,
@@ -163,6 +172,8 @@ func TestRateLimit(t *testing.T) {
 		mctrl.Finish()
 	}()
 
+	util.WaitUntil(10*time.Millisecond, 2*time.Second, func() (bool, error) { return o.PRC.Started(), nil })
+
 	var res *pb.TellRes
 	var err error
 	for i := 0; i < 10; i++ {
@@ -203,6 +214,8 @@ func TestSecureRpcPingPong(t *testing.T) {
 		s.Stop()
 	}()
 
+	util.WaitUntil(10*time.Millisecond, 2*time.Second, func() (bool, error) { return o.PRC.Started(), nil })
+
 	pong, err := p.Ping(&pb.Ping{Nonce: uint64(4689), Addr: "127.0.0.1:10001"})
 	assert.Nil(t, err)
 	assert.NotNil(t, pong)
@@ -214,7 +227,7 @@ func TestSecureRpcPingPong(t *testing.T) {
 }
 
 func TestKeepaliveParams(t *testing.T) {
-	// This only verfies the config doesn't break connections
+	// This only verifies the config doesn't break connections
 	config := LoadTestConfig("", true)
 	config.KLClientParams.Time = 50 * time.Millisecond
 	config.KLClientParams.Timeout = 20 * time.Millisecond
@@ -234,6 +247,8 @@ func TestKeepaliveParams(t *testing.T) {
 		s.Stop()
 	}()
 
+	util.WaitUntil(10*time.Millisecond, 2*time.Second, func() (bool, error) { return o.PRC.Started(), nil })
+
 	for i := 0; i < 5; i++ {
 		time.Sleep(100 * time.Millisecond)
 		pong, err := p.Ping(&pb.Ping{Nonce: uint64(4689), Addr: "127.0.0.1:10001"})
```
