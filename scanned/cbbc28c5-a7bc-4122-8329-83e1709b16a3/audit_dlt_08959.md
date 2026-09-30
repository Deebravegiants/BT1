# [?] fix data race in bft deliverer (#5464)

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2026-05-10
Source: https://github.com/hyperledger/fabric/commit/dadd7399d1fc16d4c66ee3fa3d1f5a983f281a55
Type: security-commit

## Details
fix data race in bft deliverer (#5464)

Signed-off-by: Fedor Partanskiy <fredprtnsk@gmail.com>

## Patch
### common/deliverclient/blocksprovider/bft_deliverer.go
```diff
@@ -177,7 +177,7 @@ func (d *BFTDeliverer) DeliverBlocks() {
 		// waiting for it to be consumed. A block receiver is created within.
 		d.fetchErrorsC = make(chan error, 1)
 		source := d.fetchSources[d.fetchSourceIndex]
-		go d.FetchBlocks(source)
+		go d.FetchBlocks(source, d.fetchErrorsC)
 
 		// Create and start a censorship monitor.
 		d.censorshipMonitor = d.CensorshipDetectorFactory.Create(
@@ -326,28 +326,28 @@ func (d *BFTDeliverer) Stop() {
 	d.blockReceiver.Stop()
 }
 
-func (d *BFTDeliverer) FetchBlocks(source *orderers.Endpoint) {
+func (d *BFTDeliverer) FetchBlocks(source *orderers.Endpoint, fetchErrorsC chan<- error) {
 	d.Logger.Debugf("Trying to fetch blocks from orderer: %s", source.Address)
 
 	for {
 		select {
 		case <-d.DoneC:
-			d.fetchErrorsC <- &ErrStopping{Message: "stopping"}
+			fetchErrorsC <- &ErrStopping{Message: "stopping"}
 			return
 		default:
 		}
 
 		seekInfoEnv, err := d.requester.SeekInfoBlocksFrom(d.getNextBlockNumber())
 		if err != nil {
 			d.Logger.Errorf("Could not create a signed Deliver SeekInfo message, something is critically wrong: %s", err)
-			d.fetchErrorsC <- &ErrFatal{Message: fmt.Sprintf("could not create a signed Deliver SeekInfo message: %s", err)}
+			fetchErrorsC <- &ErrFatal{Message: fmt.Sprintf("could not create a signed Deliver SeekInfo message: %s", err)}
 			return
 		}
 
 		deliverClient, cancel, err := d.requester.Connect(seekInfoEnv, source)
 		if err != nil {
 			d.Logger.Warningf("Could not connect to ordering service: %s", err)
-			d.fetchErrorsC <- errors.Wrapf(err, "could not connect to ordering service, orderer-address: %s", source.Address)
+			fetchErrorsC <- errors.Wrapf(err, "could not connect to ordering service, orderer-address: %s", source.Address)
 			return
 		}
 
@@ -364,6 +364,9 @@ func (d *BFTDeliverer) FetchBlocks(source *orderers.Endpoint) {
 		}
 
 		d.mutex.Lock()
+		if d.blockReceiver != nil {
+			d.blockReceiver.Stop()
+		}
 		d.blockReceiver = blockRcv
 		d.mutex.Unlock()
 
@@ -378,10 +381,10 @@ func (d *BFTDeliverer) FetchBlocks(source *orderers.Endpoint) {
 				d.Logger.Debugf("BlockReceiver stopped while processing incoming blocks: %s", errProc)
 			case *errRefreshEndpoint:
 				d.Logger.Infof("Endpoint refreshed while processing incoming blocks: %s", errProc)
-				d.fetchErrorsC <- errProc
+				fetchErrorsC <- errProc
 			default:
 				d.Logger.Warningf("Failure while processing incoming blocks: %s", errProc)
-				d.fetchErrorsC <- errProc
+				fetchErrorsC <- errProc
 			}
 
 			return
```

### common/deliverclient/blocksprovider/bft_deliverer_test.go
```diff
@@ -32,6 +32,8 @@ import (
 	"google.golang.org/protobuf/proto"
 )
 
+var logger = flogging.MustGetLogger("BFTDeliverer.test")
+
 type bftDelivererTestSetup struct {
 	gWithT *WithT
 	d      *blocksprovider.BFTDeliverer
@@ -63,6 +65,7 @@ type bftDelivererTestSetup struct {
 	monErrC       chan error                 // the monitor errors channel, where it emits (fake) censorship events
 	monDoneC      chan struct{}              // signal the monitor to stop
 	monEndC       chan struct{}              // when the monitor stops, it closes this channel
+	logger        *flogging.FabricLogger
 }
 
 func newBFTDelivererTestSetup(t *testing.T) *bftDelivererTestSetup {
@@ -83,6 +86,7 @@ func newBFTDelivererTestSetup(t *testing.T) *bftDelivererTestSetup {
 		deliverClientDoneC:                 make(chan struct{}),
 		recvStepC:                          make(chan *orderer.DeliverResponse),
 		endC:                               make(chan struct{}),
+		logger:                             logger.With("name", t.Name()),
 	}
 
 	return s
@@ -220,7 +224,7 @@ func (s *bftDelivererTestSetup) initialize(t *testing.T) {
 		Signer:                          s.fakeSigner,
 		DeliverStreamer:                 s.fakeDeliverStreamer,
 		CensorshipDetectorFactory:       s.fakeCensorshipMonFactory,
-		Logger:                          flogging.MustGetLogger("BFTDeliverer.test"),
+		Logger:                          s.logger,
 		TLSCertHash:                     []byte("tls-cert-hash"),
 		MaxRetryInterval:                10 * time.Second,
 		InitialRetryInterval:            100 * time.Millisecond,
@@ -272,18 +276,18 @@ func TestBFTDeliverer_NoBlocks(t *testing.T) {
 	startTime := time.Now()
 	setup.start()
 
-	t.Log("Checks the ledger height")
+	setup.logger.Info("Checks the ledger height")
 	require.Eventually(t, func() bool {
 		return setup.fakeLedgerInfo.LedgerHeightCallCount() == 1
 	}, eventuallyTO, 10*time.Millisecond)
 
-	t.Log("Get the endpoints")
+	setup.logger.Info("Get the endpoints")
 	setup.gWithT.Eventually(setup.fakeOrdererConnectionSource.ShuffledEndpointsCallCount, eventuallyTO).Should(Equal(1))
 
-	t.Log("Signs the seek request")
+	setup.logger.Info("Signs the seek request")
 	setup.gWithT.Eventually(setup.fakeSigner.SignCallCount, eventuallyTO).Should(Equal(1))
 
-	t.Log("Seeks the correct block")
+	setup.logger.Info("Seeks the correct block")
 	setup.gWithT.Eventually(setup.fakeDeliverClient.SendCallCount, eventuallyTO).Should(Equal(1))
 	env := setup.fakeDeliverClient.SendArgsForCall(0)
 	require.True(t, bytes.Equal(env.GetSignature(), []byte("good-sig")))
@@ -294,17 +298,17 @@ func TestBFTDeliverer_NoBlocks(t *testing.T) {
 	require.NoError(t, err)
 	require.Equal(t, uint64(7), seekInfo.GetStart().GetSpecified().GetNumber())
 
-	t.Log("Creates and starts the monitor")
+	setup.logger.Info("Creates and starts the monitor")
 	setup.gWithT.Eventually(setup.fakeCensorshipMonFactory.CreateCallCount, eventuallyTO).Should(Equal(1))
 	setup.assertEventuallyMonitorCallCount(1)
 
-	t.Log("Dials to an orderer from the shuffled endpoints")
+	setup.logger.Info("Dials to an orderer from the shuffled endpoints")
 	setup.gWithT.Eventually(setup.fakeDialer.DialCallCount, eventuallyTO).Should(Equal(1))
 	addr, tlsCerts := setup.fakeDialer.DialArgsForCall(0)
 	require.Equal(t, "orderer-address-1", addr)
 	require.Nil(t, tlsCerts) // TODO add tests that verify this
 
-	t.Log("waits patiently for new blocks from the orderer")
+	setup.logger.Info("waits patiently for new blocks from the orderer")
 	require.Condition(t, func() (success bool) {
 		select {
 		case <-setup.endC:
@@ -316,12 +320,12 @@ func TestBFTDeliverer_NoBlocks(t *testing.T) {
 		}
 	}, "channels wrongly closed")
 
-	t.Log("block progress is reported correctly")
+	setup.logger.Info("block progress is reported correctly")
 	bNum, bTime := setup.d.BlockProgress()
 	require.Equal(t, uint64(6), bNum)
 	require.True(t, bTime.After(startTime))
 
-	t.Log("client connection is active")
+	setup.logger.Info("client connection is active")
 	func() {
 		setup.mutex.Lock()
 		defer setup.mutex.Unlock()
@@ -340,7 +344,7 @@ func TestBFTDeliverer_FatalErrors(t *testing.T) {
 		setup.fakeLedgerInfo.LedgerHeightReturns(0, fmt.Errorf("fake-ledger-error"))
 		setup.start()
 
-		t.Log("Exits the DeliverBlocks loop")
+		setup.logger.Info("Exits the DeliverBlocks loop")
 		setup.gWithT.Eventually(setup.endC, eventuallyTO).Should(BeClosed())
 		require.Equal(t, 0, setup.fakeCensorshipMonFactory.CreateCallCount(), "monitor was not created")
 
@@ -354,11 +358,11 @@ func TestBFTDeliverer_FatalErrors(t *testing.T) {
 		setup.fakeSigner.SignReturns(nil, fmt.Errorf("fake-ledger-error"))
 		setup.start()
 
-		t.Log("Starts the DeliverBlocks and Monitor loop")
+		setup.logger.Info("Starts the DeliverBlocks and Monitor loop")
 		setup.gWithT.Eventually(setup.fakeCensorshipMonFactory.CreateCallCount, eventuallyTO).Should(Equal(1))
 		setup.assertEventuallyMonitorCallCount(1)
 
-		t.Log("Exits the DeliverBlocks and Monitor loop")
+		setup.logger.Info("Exits the DeliverBlocks and Monitor loop")
 		setup.gWithT.Eventually(setup.endC, eventuallyTO).Should(BeClosed())
 		setup.gWithT.Eventually(setup.monEndC, eventuallyTO).Should(BeClosed())
 
@@ -371,9 +375,9 @@ func TestBFTDeliverer_FatalErrors(t *testing.T) {
 		setup.fakeOrdererConnectionSource.ShuffledEndpointsReturns(nil)
 		setup.start()
 
-		t.Log("Starts the DeliverBlocks and Monitor loop")
+		setup.logger.Info("Starts the DeliverBlocks and Monitor loop")
 		setup.gWithT.Eventually(setup.fakeOrdererConnectionSource.ShuffledEndpointsCallCount, eventuallyTO).Should(Equal(1))
-		t.Log("Exits the DeliverBlocks loop")
+		setup.logger.Info("Exits the DeliverBlocks loop")
 		setup.gWithT.Eventually(setup.endC).Should(BeClosed())
 		setup.gWithT.Eventually(setup.fakeCensorshipMonFactory.CreateCallCount, eventuallyTO).Should(Equal(0))
 		require.Nil(t, setup.fakeCensorshipMon)
@@ -434,7 +438,7 @@ func TestBFTDeliverer_DialRetries(t *testing.T) {
 		setup.gWithT.Eventually(setup.fakeDialer.DialCallCount, eventuallyTO).Should(Equal(25))
 		setup.gWithT.Expect(setup.fakeSleeper.SleepCallCount()).To(Equal(24))
 
-		t.Log("Exponential backoff after every round")
+		setup.logger.Info("Exponential backoff after every round")
 		minDur := 100 * time.Millisecond
 		for i := range 24 {
 			round := (i + 1) / 4
@@ -454,7 +458,7 @@ func TestBFTDeliverer_DialRetries(t *testing.T) {
 			require.Equal(t, 1, mon.StopCallCount())
 		}
 
-		t.Log("Cycles through all sources")
+		setup.logger.Info("Cycles through all sources")
 		addresses := make(map[string]bool)
 		addr1, _ := setup.fakeDialer.DialArgsForCall(0)
 		for i := 1; i < setup.fakeDialer.DialCallCount(); i++ {
@@ -475,12 +479,12 @@ func TestBFTDeliverer_DialRetries(t *testing.T) {
 
 		setup.start()
 		setup.gWithT.Eventually(setup.fakeDialer.DialCallCount, eventuallyTO).Should(BeNumerically(">=", 100))
-		t.Log("Calls the handler but does not stop")
+		setup.logger.Info("Calls the handler but does not stop")
 		setup.gWithT.Eventually(setup.fakeDurationExceededHandler.DurationExceededHandlerCallCount, eventuallyTO).Should(BeNumerically(">", 5))
 		setup.gWithT.Consistently(setup.endC).ShouldNot(BeClosed())
 		setup.stop()
 
-		t.Log("Exponential backoff after every round, with saturation of 10s")
+		setup.logger.Info("Exponential backoff after every round, with saturation of 10s")
 		minDur := 100 * time.Millisecond
 		for i := 0; i < setup.fakeSleeper.SleepCallCount(); i++ {
 			round := (i + 1) / 4
@@ -513,11 +517,11 @@ func TestBFTDeliverer_DialRetries(t *testing.T) {
 		setup.fakeDialer.DialReturns(nil, fmt.Errorf("fake-dial-error"))
 
 		setup.start()
-		t.Log("Calls handler and stops")
+		setup.logger.Info("Calls handler and stops")
 		setup.gWithT.Eventually(setup.fakeDurationExceededHandler.DurationExceededHandlerCallCount, eventuallyTO).Should(Equal(1))
 		setup.gWithT.Eventually(setup.endC, eventuallyTO).Should(BeClosed())
 
-		t.Log("Exponential backoff after every round, with saturation of 10s")
+		setup.logger.Info("Exponential backoff after every round, with saturation of 10s")
 		minDur := 100 * time.Millisecond
 		totalDur := time.Duration(0)
 		for i := 0; i < setup.fakeSleeper.SleepCallCount(); i++ {
@@ -596,7 +600,7 @@ func TestBFTDeliverer_DeliverRetries(t *testing.T) {
 		setup.gWithT.Eventually(setup.fakeDialer.DialCallCount, eventuallyTO).Should(Equal(25))
 		setup.gWithT.Expect(setup.fakeSleeper.SleepCallCount()).To(Equal(24))
 
-		t.Log("Exponential backoff after every round")
+		setup.logger.Info("Exponential backoff after every round")
 		minDur := 100 * time.Millisecond
 		for i := range 24 {
 			round := (i + 1) / 4
@@ -616,7 +620,7 @@ func TestBFTDeliverer_DeliverRetries(t *testing.T) {
 			require.Equal(t, 1, mon.StopCallCount(), fmt.Sprintf("i=%d", i))
 		}
 
-		t.Log("Cycles through all sources")
+		setup.logger.Info("Cycles through all sources")
 		addresses := make(map[string]bool)
 		addr1, _ := setup.fakeDialer.DialArgsForCall(0)
 		for i := 1; i < setup.fakeDialer.DialCallCount(); i++ {
@@ -639,7 +643,7 @@ func TestBFTDeliverer_DeliverRetries(t *testing.T) {
 		setup.gWithT.Eventually(setup.fakeDialer.DialCallCount, eventuallyTO).Should(BeNumerically(">=", 40))
 		setup.stop()
 
-		t.Log("Exponential backoff after every round, with saturation of 10s")
+		setup.logger.Info("Exponential backoff after every round, with saturation of 10s")
 		minDur := 100 * time.Millisecond
 		for i := 0; i < setup.fakeSleeper.SleepCallCount(); i++ {
 			round := (i + 1) / 4
@@ -670,7 +674,7 @@ func TestBFTDeliverer_BlockReception(t *testing.T) {
 		setup.initialize(t)
 		startTime := time.Now()
 
-		t.Log("block progress is reported correctly before start")
+		setup.logger.Info("block progress is reported correctly before start")
 		bNum, bTime := setup.d.BlockProgress()
 		require.Equal(t, uint64(0), bNum)
 		require.True(t, bTime.IsZero())
@@ -682,32 +686,32 @@ func TestBFTDeliverer_BlockReception(t *testing.T) {
 		require.Equal(t, uint64(6), bNum)
 		require.True(t, bTime.After(startTime))
 
-		t.Log("Recv() returns a single block, num: 7")
+		setup.logger.Info("Recv() returns a single block, num: 7")
 		setup.recvStepC <- &orderer.DeliverResponse{
 			Type: &orderer.DeliverResponse_Block{
 				Block: &common.Block{Header: &common.BlockHeader{Number: 7}},
 			},
 		}
 
-		t.Log("receives the block and loops, not sleeping")
+		setup.logger.Info("receives the block and loops, not sleeping")
 		setup.gWithT.Eventually(setup.fakeDeliverClient.RecvCallCount, eventuallyTO).Should(Equal(2))
 		require.Equal(t, 0, setup.fakeSleeper.SleepCallCount())
 
-		t.Log("checks the validity of the block")
+		setup.logger.Info("checks the validity of the block")
 		setup.gWithT.Eventually(setup.fakeUpdatableBlockVerifier.VerifyBlockCallCount, eventuallyTO).Should(Equal(1))
 		block := setup.fakeUpdatableBlockVerifier.VerifyBlockArgsForCall(0)
 		require.True(t, proto.Equal(block, &common.Block{Header: &common.BlockHeader{Number: 7}}))
 
-		t.Log("handle the block")
+		setup.logger.Info("handle the block")
 		setup.gWithT.Eventually(setup.fakeBlockHandler.HandleBlockCallCount, eventuallyTO).Should(Equal(1))
 		channelName, block2 := setup.fakeBlockHandler.HandleBlockArgsForCall(0)
 		require.Equal(t, "channel-id", channelName)
 		require.True(t, proto.Equal(block2, &common.Block{Header: &common.BlockHeader{Number: 7}}))
 
-		t.Log("does not update config on verifier")
+		setup.logger.Info("does not update config on verifier")
 		require.Equal(t, 0, setup.fakeUpdatableBlockVerifier.UpdateConfigCallCount())
 
-		t.Log("block progress is reported correctly")
+		setup.logger.Info("block progress is reported correctly")
 		setup.gWithT.Eventually(
 			func() bool {
 				bNum2, bTime2 := setup.d.BlockProgress()
@@ -722,20 +726,20 @@ func TestBFTDeliverer_BlockReception(t *testing.T) {
 		setup := newBFTDelivererTestSetup(t)
 		setup.initialize(t)
 
-		t.Log("block verification fails")
+		setup.logger.Info("block verification fails")
 		setup.fakeUpdatableBlockVerifier.VerifyBlockReturns(fmt.Errorf("fake-verify-error"))
 
 		startTime := time.Now()
 		setup.start()
 
-		t.Log("Recv() returns a single block, num: 7")
+		setup.logger.Info("Recv() returns a single block, num: 7")
 		setup.recvStepC <- &orderer.DeliverResponse{
 			Type: &orderer.DeliverResponse_Block{
 				Block: &common.Block{Header: &common.BlockHeader{Number: 7}},
 			},
 		}
 
-		t.Log("disconnects, sleeps, and tries again")
+		setup.logger.Info("disconnects, sleeps, and tries again")
 		setup.gWithT.Eventually(setup.fakeUpdatableBlockVerifier.VerifyBlockCallCount, eventuallyTO).Should(Equal(1))
 		setup.gWithT.Eventually(setup.fakeSleeper.SleepCallCount, eventuallyTO).Should(Equal(1))
 		require.Equal(t, 1, setup.fakeDeliverClient.CloseSendCallCount())
@@ -752,10 +756,10 @@ func TestBFTDeliverer_BlockReception(t *testing.T) {
 			require.Len(t, setup.monitorSet, 2)
 		}()
 
-		t.Log("does not handle the block")
+		setup.logger.Info("does not handle the block")
 		require.Equal(t, 0, setup.fakeBlockHandler.HandleBlockCallCount())
 
-		t.Log("block progress is reported correctly")
+		setup.logger.Info("block progress is reported correctly")
 		bNum, bTime := setup.d.BlockProgress()
 		require.Equal(t, uint64(6), bNum)
 		require.True(t, bTime.After(startTime))
@@ -768,20 +772,20 @@ func TestBFTDeliverer_BlockReception(t *testing.T) {
 		setup := newBFTDelivererTestSetup(t)
 		setup.initialize(t)
 
-		t.Log("block verification fails")
+		setup.logger.Info("block verification fails")
 		setup.fakeBlockHandler.HandleBlockReturns(fmt.Errorf("block-handling-error"))
 
 		startTime := time.Now()
 		setup.start()
 
-		t.Log("Recv() returns a single block, num: 7")
+		setup.logger.Info("Recv() returns a single block, num: 7")
 		setup.recvStepC <- &orderer.DeliverResponse{
 			Type: &orderer.DeliverResponse_Block{
 				Block: &common.Block{Header: &common.BlockHeader{Number: 7}},
 			},
 		}
 
-		t.Log("disconnects, sleeps, and tries again")
+		setup.logger.Info("disconnects, sleeps, and tries again")
 		setup.gWithT.Eventually(setup.fakeUpdatableBlockVerifier.VerifyBlockCallCount, eventuallyTO).Should(Equal(1))
 		setup.gWithT.Eventually(setup.fakeSleeper.SleepCallCount, eventuallyTO).Should(Equal(1))
 		require.Equal(t, 1, setup.fakeDeliverClient.CloseSendCallCount())
@@ -799,10 +803,10 @@ func TestBFTDeliverer_BlockReception(t *testing.T) {
 			require.Len(t, setup.monitorSet, 2)
 		}()
 
-		t.Log("handle the block")
+		setup.logger.Info("handle the block")
 		require.Equal(t, 1, setup.fakeBlockHandler.HandleBlockCallCount())
 
-		t.Log("block progress is reported correctly")
+		setup.logger.Info("block progress is reported correctly")
 		bNum, bTime := setup.d.BlockProgress()
 		require.Equal(t, uint64(6), bNum)
 		require.True(t, bTime.After(startTime) || bTime.Equal(startTime))
@@ -832,45 +836,45 @@ func TestBFTDeliverer_BlockReception(t *testing.T) {
 		setup.gWithT.Eventually(setup.fakeDialer.DialCallCount, eventuallyTO).Should(Equal(25))
 		setup.gWithT.Expect(setup.fakeSleeper.SleepCallCount()).To(Equal(24))
 
-		t.Log("Recv() returns a single block, num: 7")
+		setup.logger.Info("Recv() returns a single block, num: 7")
 		setup.recvStepC <- &orderer.DeliverResponse{
 			Type: &orderer.DeliverResponse_Block{
 				Block: &common.Block{Header: &common.BlockHeader{Number: 7}},
 			},
 		}
 
-		t.Log("receives the block and loops, not sleeping")
+		setup.logger.Info("receives the block and loops, not sleeping")
 		setup.gWithT.Eventually(setup.fakeDeliverClient.RecvCallCount, eventuallyTO).Should(Equal(2))
 		require.Equal(t, 24, setup.fakeSleeper.SleepCallCount())
 
-		t.Log("checks the validity of the block")
+		setup.logger.Info("checks the validity of the block")
 		setup.gWithT.Eventually(setup.fakeUpdatableBlockVerifier.VerifyBlockCallCount, eventuallyTO).Should(Equal(1))
 		block := setup.fakeUpdatableBlockVerifier.VerifyBlockArgsForCall(0)
 		require.True(t, proto.Equal(block, &common.Block{Header: &common.BlockHeader{Number: 7}}))
 
-		t.Log("handle the block")
+		setup.logger.Info("handle the block")
 		setup.gWithT.Eventually(setup.fakeBlockHandler.HandleBlockCallCount, eventuallyTO).Should(Equal(1))
 		channelName, block2 := setup.fakeBlockHandler.HandleBlockArgsForCall(0)
 		require.Equal(t, "channel-id", channelName)
 		require.True(t, proto.Equal(block2, &common.Block{Header: &common.BlockHeader{Number: 7}}))
 
-		t.Log("block progress is reported correctly")
+		setup.logger.Info("block progress is reported correctly")
 		require.Eventually(t, func() bool {
 			bNum, bTime := setup.d.BlockProgress()
 			return uint64(7) == bNum && bTime.After(startTime)
 		}, eventuallyTO, 10*time.Millisecond)
 
 		setup.gWithT.Expect(setup.fakeDialer.DialCallCount()).Should(Equal(25))
 
-		t.Log("a Recv() error occurs")
+		setup.logger.Info("a Recv() error occurs")
 		setup.fakeDeliverClient.CloseSendStub = nil
 		setup.recvStepC <- nil
 
 		setup.gWithT.Eventually(setup.fakeCensorshipMonFactory.CreateCallCount, eventuallyTO).Should(Equal(26))
 		setup.gWithT.Eventually(setup.fakeDialer.DialCallCount, eventuallyTO).Should(Equal(26))
 		setup.gWithT.Expect(setup.fakeSleeper.SleepCallCount()).To(Equal(25))
 
-		t.Log("failure count was reset, sleep duration returned to minimum")
+		setup.logger.Info("failure count was reset, sleep duration returned to minimum")
 		require.Equal(t, 6400*time.Millisecond, setup.fakeSleeper.SleepArgsForCall(23))
 		require.Equal(t, 100*time.Millisecond, setup.fakeSleeper.SleepArgsForCall(24))
 
@@ -909,41 +913,41 @@ func TestBFTDeliverer_BlockReception(t *testing.T) {
 		setup.gWithT.Eventually(setup.fakeDialer.DialCallCount, eventuallyTO).Should(Equal(81))
 		setup.gWithT.Expect(setup.fakeSleeper.SleepCallCount()).To(Equal(80))
 
-		t.Log("Recv() returns a single block, num: 7")
+		setup.logger.Info("Recv() returns a single block, num: 7")
 		setup.recvStepC <- &orderer.DeliverResponse{
 			Type: &orderer.DeliverResponse_Block{
 				Block: &common.Block{Header: &common.BlockHeader{Number: 7}},
 			},
 		}
 
-		t.Log("receives the block and loops, not sleeping")
+		setup.logger.Info("receives the block and loops, not sleeping")
 		setup.gWithT.Eventually(setup.fakeDeliverClient.RecvCallCount, eventuallyTO).Should(Equal(2))
 		require.Equal(t, 80, setup.fakeSleeper.SleepCallCount())
 
-		t.Log("a Recv() error occurs, more dial attempts")
+		setup.logger.Info("a Recv() error occurs, more dial attempts")
 		setup.fakeDeliverClient.CloseSendStub = nil
 		setup.recvStepC <- nil
 		setup.gWithT.Eventually(setup.fakeDialer.DialCallCount, eventuallyTO).Should(Equal(161))
 		setup.gWithT.Expect(setup.fakeSleeper.SleepCallCount()).To(Equal(160))
 
-		t.Log("Recv() returns a single block, num: 8")
+		setup.logger.Info("Recv() returns a single block, num: 8")
 		setup.recvStepC <- &orderer.DeliverResponse{
 			Type: &orderer.DeliverResponse_Block{
 				Block: &common.Block{Header: &common.BlockHeader{Number: 8}},
 			},
 		}
 
-		t.Log("receives the block and loops, not sleeping")
+		setup.logger.Info("receives the block and loops, not sleeping")
 		setup.gWithT.Eventually(setup.fakeDeliverClient.RecvCallCount, eventuallyTO).Should(Equal(4))
 		require.Equal(t, 160, setup.fakeSleeper.SleepCallCount())
 
-		t.Log("a Recv() error occurs, more dial attempts")
+		setup.logger.Info("a Recv() error occurs, more dial attempts")
 		setup.fakeDeliverClient.CloseSendStub = nil
 		setup.recvStepC <- nil
 		setup.gWithT.Eventually(setup.fakeDialer.DialCallCount, eventuallyTO).Should(Equal(241))
 		setup.gWithT.Expect(setup.fakeSleeper.SleepCallCount()).To(Equal(240))
 
-		t.Log("DurationExceededHandler handler is never called, DeliverBlocks() does not stop")
+		setup.logger.Info("DurationExceededHandler handler is never called, DeliverBlocks() does not stop")
 		setup.gWithT.Expect(setup.fakeDurationExceededHandler.DurationExceededHandlerCallCount()).To(Equal(0))
 		setup.gWithT.Consistently(setup.endC).ShouldNot(BeClosed())
 
@@ -957,7 +961,7 @@ func TestBFTDeliverer_BlockReception(t *testing.T) {
 		setup.gWithT.Eventually(setup.fakeOrdererConnectionSource.UpdateCallCount, eventuallyTO).Should(Equal(1))
 		startTime := time.Now()
 
-		t.Log("block progress is reported correctly before start")
+		setup.logger.Info("block progress is reported correctly before start")
 		bNum, bTime := setup.d.BlockProgress()
 		require.Equal(t, uint64(0), bNum)
 		require.True(t, bTime.IsZero())
@@ -969,7 +973,7 @@ func TestBFTDeliverer_BlockReception(t *testing.T) {
 		require.Equal(t, uint64(6), bNum)
 		require.True(t, bTime.After(startTime))
 
-		t.Log("Recv() returns a single config block, num: 7")
+		setup.logger.Info("Recv() returns a single config block, num: 7")
 		env := &common.Envelope{
 			Payload: protoutil.MarshalOrPanic(&common.Payload{
 				Header: &common.Header{
@@ -997,11 +1001,11 @@ func TestBFTDeliverer_BlockReception(t *testing.T) {
 			},
 		}
 
-		t.Log("receives the block and loops, not sleeping")
+		setup.logger.Info("receives the block and loops, not sleeping")
 		setup.gWithT.Eventually(setup.fakeDeliverClient.RecvCallCount, eventuallyTO).Should(Equal(2))
 		require.Equal(t, 0, setup.fakeSleeper.SleepCallCount())
 
-		t.Log("checks the validity of the block")
+		setup.logger.Info("checks the validity of the block")
 		setup.gWithT.Eventually(setup.fakeUpdatableBlockVerifier.VerifyBlockCallCount, eventuallyTO).Should(Equal(1))
 		block := setup.fakeUpdatableBlockVerifier.VerifyBlockArgsForCall(0)
 		require.True(t, proto.Equal(block,
@@ -1012,7 +1016,7 @@ func TestBFTDeliverer_BlockReception(t *testing.T) {
 				},
 			}))
 
-		t.Log("handle the block")
+		setup.logger.Info("handle the block")
 		setup.gWithT.Eventually(setup.fakeBlockHandler.HandleBlockCallCount, eventuallyTO).Should(Equal(1))
 		channelName, block2 := setup.fakeBlockHandler.HandleBlockArgsForCall(0)
 		require.Equal(t, "channel-id", channelName)
@@ -1024,16 +1028,16 @@ func TestBFTDeliverer_BlockReception(t *testing.T) {
 				},
 			}))
 
-		t.Log("update config on verifier")
+		setup.logger.Info("update config on verifier")
 		setup.gWithT.Eventually(setup.fakeUpdatableBlockVerifier.UpdateConfigCallCount, eventuallyTO).Should(Equal(1))
 
-		t.Log("block progress is reported correctly")
+		setup.logger.Info("block progress is reported correctly")
 		require.Eventually(t, func() bool {
 			bNum2, bTime2 := setup.d.BlockProgress()
 			return uint64(7) == bNum2 && bTime2.After(bTime)
 		}, eventuallyTO, 100*time.Millisecond)
 
-		t.Log("updated orderer source")
+		setup.logger.Info("updated orderer source")
 		setup.gWithT.Eventually(setup.fakeOrdererConnectionSource.UpdateCallCount, eventuallyTO).Should(Equal(2))
 
 		setup.stop()
@@ -1053,15 +1057,15 @@ func TestBFTDeliverer_CensorshipMonitorEvents(t *testing.T) {
 			setup.gWithT.Eventually(setup.fakeDialer.DialCallCount, eventuallyTO).Should(Equal(1))
 
 			// var mon *fake.CensorshipDetector
-			t.Logf("monitor error channel returns unexpected value: %v", errVal)
+			setup.logger.Infof("monitor error channel returns unexpected value: %v", errVal)
 			func() {
 				setup.mutex.Lock()
 				defer setup.mutex.Unlock()
 
 				setup.monErrC <- errVal
 			}()
 
-			t.Logf("monitor and deliverer exit the loop")
+			setup.logger.Infof("monitor and deliverer exit the loop")
 			<-setup.endC
 			<-setup.monEndC
 
@@ -1079,7 +1083,7 @@ func TestBFTDeliverer_CensorshipMonitorEvents(t *testing.T) {
 		setup.gWithT.Eventually(setup.fakeCensorshipMonFactory.CreateCallCount, eventuallyTO).Should(Equal(1))
 		setup.gWithT.Eventually(setup.fakeDialer.DialCallCount, eventuallyTO).Should(Equal(1))
 
-		t.Log("monitor error channel returns censorship error")
+		setup.logger.Info("monitor error channel returns censorship error")
 		func() {
 			setup.mutex.Lock()
 			defer setup.mutex.Unlock()
@@ -1104,10 +1108,10 @@ func TestBFTDeliverer_CensorshipMonitorEvents(t *testing.T) {
 		setup.start()
 
 		for n := 1; n <= 40; n++ {
-			setup.gWithT.Eventually(setup.fakeCensorshipMonFactory.CreateCallCount, eventuallyTO).Should(Equal(n))
-			setup.gWithT.Eventually(setup.fakeDialer.DialCallCount, eventuallyTO).Should(Equal(n))
+			setup.gWithT.Eventually(setup.fakeCensorshipMonFactory.CreateCallCount, eventuallyTO).Should(Equal(n), "setup.fakeCensorshipMonFactory.CreateCallCount-1")
+			setup.gWithT.Eventually(setup.fakeDialer.DialCallCount, eventuallyTO).Should(Equal(n), "setup.fakeDialer.DialCallCount-1")
 
-			t.Logf("monitor error channel returns censorship error num: %d", n)
+			setup.logger.Infof("monitor error channel returns censorship error num: %d", n)
 			func() {
 				setup.mutex.Lock()
 				defer setup.mutex.Unlock()
@@ -1121,14 +1125,14 @@ func TestBFTDeliverer_CensorshipMonitorEvents(t *testing.T) {
 
 				return len(setup.monitorSet)
 			}
-			setup.gWithT.Eventually(numMon, eventuallyTO).Should(Equal(n + 1))
+			setup.gWithT.Eventually(numMon, eventuallyTO).Should(Equal(n+1), "numMon")
 
-			setup.gWithT.Eventually(setup.fakeDialer.DialCallCount, eventuallyTO).Should(Equal(n + 1))
-			setup.gWithT.Expect(setup.fakeSleeper.SleepCallCount()).To(Equal(n))
-			setup.gWithT.Eventually(setup.fakeCensorshipMonFactory.CreateCallCount, eventuallyTO).Should(Equal(n + 1))
+			setup.gWithT.Eventually(setup.fakeDialer.DialCallCount, eventuallyTO).Should(Equal(n+1), "setup.fakeDialer.DialCallCount-2")
+			setup.gWithT.Expect(setup.fakeSleeper.SleepCallCount()).To(Equal(n), "setup.fakeSleeper.SleepCallCount")
+			setup.gWithT.Eventually(setup.fakeCensorshipMonFactory.CreateCallCount, eventuallyTO).Should(Equal(n+1), "setup.fakeCensorshipMonFactory.CreateCallCount-2")
 		}
 
-		t.Log("Exponential backoff after every round, with saturation")
+		setup.logger.Info("Exponential backoff after every round, with saturation")
 		minDur := 100 * time.Millisecond
 		for i := range 40 {
 			round := (i + 1) / 4
@@ -1147,7 +1151,7 @@ func TestBFTDeliverer_CensorshipMonitorEvents(t *testing.T) {
 			require.Equal(t, 1, mon.StopCallCount())
 		}
 
-		t.Log("Cycles through all sources")
+		setup.logger.Info("Cycles through all sources")
 		addresses := make(map[string]bool)
 		addr1, _ := setup.fakeDialer.DialArgsForCall(0)
 		for i := 1; i < setup.fakeDialer.DialCallCount(); i++ {
@@ -1214,27 +1218,27 @@ func TestBFTDeliverer_RefreshEndpoints(t *testing.T) {
 
 	setup.start()
 
-	t.Log("Get the endpoints")
+	setup.logger.Info("Get the endpoints")
 	setup.gWithT.Eventually(setup.fakeOrdererConnectionSource.ShuffledEndpointsCallCount, eventuallyTO).Should(Equal(1))
 
-	t.Log("Creates and starts the monitor")
+	setup.logger.Info("Creates and starts the monitor")
 	setup.gWithT.Eventually(setup.fakeCensorshipMonFactory.CreateCallCount, eventuallyTO).Should(Equal(1))
 	setup.assertEventuallyMonitorCallCount(1)
 
-	t.Log("Dials to an orderer from the shuffled endpoints of the first set")
+	setup.logger.Info("Dials to an orderer from the shuffled endpoints of the first set")
 	setup.gWithT.Eventually(setup.fakeDialer.DialCallCount, eventuallyTO).Should(Equal(1))
 	addr, _ := setup.fakeDialer.DialArgsForCall(0)
 	require.Equal(t, "orderer-address-1", addr)
 
-	t.Log("Closing the refresh channel (always on all endpoints)")
+	setup.logger.Info("Closing the refresh channel (always on all endpoints)")
 	for _, s := range sources1 {
 		close(s.Refreshed)
 	}
 
-	t.Log("Get the endpoints again")
+	setup.logger.Info("Get the endpoints again")
 	setup.gWithT.Eventually(setup.fakeOrdererConnectionSource.ShuffledEndpointsCallCount, eventuallyTO).Should(Equal(2))
 
-	t.Log("Creates and starts the monitor")
+	setup.logger.Info("Creates and starts the monitor")
 	setup.gWithT.Eventually(setup.fakeCensorshipMonFactory.CreateCallCount, eventuallyTO).Should(Equal(2))
 	func() {
 		setup.mutex.Lock()
@@ -1244,12 +1248,12 @@ func TestBFTDeliverer_RefreshEndpoints(t *testing.T) {
 		setup.gWithT.Eventually(setup.monitorSet[1].MonitorCallCount, eventuallyTO).Should(Equal(1))
 	}()
 
-	t.Log("Dials to an orderer from the shuffled endpoints of the second set")
+	setup.logger.Info("Dials to an orderer from the shuffled endpoints of the second set")
 	setup.gWithT.Eventually(setup.fakeDialer.DialCallCount, eventuallyTO).Should(Equal(2))
 	addr, _ = setup.fakeDialer.DialArgsForCall(1)
 	require.Equal(t, "orderer-address-5", addr)
 
-	t.Log("Does not sleep")
+	setup.logger.Info("Does not sleep")
 	require.Equal(t, 0, setup.fakeSleeper.SleepCallCount())
 
 	setup.stop()
```
