# [?] witnessbeacon: avoid interceptor deadlock

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2026-06-22
Source: https://github.com/lightningnetwork/lnd/commit/98da7b4a56a75ba2dbf47391d43229fd9696e98a
Type: security-commit

## Details
witnessbeacon: avoid interceptor deadlock

Release the preimage beacon lock before invoking the on-chain
interceptor. The interceptor path can block on the htlcswitch event
loop, while resolution of another held on-chain HTLC can call back
into the beacon to add a preimage.

If interceptor delivery fails after the subscriber was registered,
cancel the subscription before returning the error.

On-chain held entries are replay handles for the interceptor while
contractcourt waits for a preimage or on-chain expiry. Once the resolver
tears down, keeping the handle until the refund timeout can replay a stale
HTLC to a reconnecting interceptor.

Thread a dedicated cleanup signal from the witness subscription cancel path
back through the interceptable switch event loop. The held set only removes
on-chain entries for that signal, leaving off-chain entries under the link
flow lifecycle.

## Patch
### server.go
```diff
@@ -935,6 +935,7 @@ func newServer(ctx context.Context, cfg *Config, listenAddrs []net.Addr,
 	s.witnessBeacon = newPreimageBeacon(
 		dbs.ChanStateDB.NewWitnessCache(),
 		s.interceptableSwitch.ForwardPacket,
+		s.interceptableSwitch.RemoveOnChainIntercept,
 	)
 
 	chanStatusMgrCfg := &netann.ChanStatusConfig{
```

### witness_beacon.go
```diff
@@ -45,15 +45,19 @@ type preimageBeacon struct {
 	subscribers   map[uint64]*preimageSubscriber
 
 	interceptor func(htlcswitch.InterceptedForward) error
+
+	cancelInterceptor func(models.CircuitKey) error
 }
 
 func newPreimageBeacon(wCache witnessCache,
-	interceptor func(htlcswitch.InterceptedForward) error) *preimageBeacon {
+	interceptor func(htlcswitch.InterceptedForward) error,
+	cancelInterceptor func(models.CircuitKey) error) *preimageBeacon {
 
 	return &preimageBeacon{
-		wCache:      wCache,
-		interceptor: interceptor,
-		subscribers: make(map[uint64]*preimageSubscriber),
+		wCache:            wCache,
+		interceptor:       interceptor,
+		cancelInterceptor: cancelInterceptor,
+		subscribers:       make(map[uint64]*preimageSubscriber),
 	}
 }
 
@@ -65,43 +69,50 @@ func (p *preimageBeacon) SubscribeUpdates(
 	nextHopOnionBlob []byte) (*contractcourt.WitnessSubscription, error) {
 
 	p.Lock()
-	defer p.Unlock()
-
 	clientID := p.clientCounter
 	client := &preimageSubscriber{
 		updateChan: make(chan lntypes.Preimage, 10),
 		quit:       make(chan struct{}),
 	}
 
-	p.subscribers[p.clientCounter] = client
+	p.subscribers[clientID] = client
 
 	p.clientCounter++
+	p.Unlock()
 
 	srvrLog.Debugf("Creating new witness beacon subscriber, id=%v",
-		p.clientCounter)
+		clientID)
+
+	inKey := models.CircuitKey{
+		ChanID: chanID,
+		HtlcID: htlc.HtlcIndex,
+	}
 
 	sub := &contractcourt.WitnessSubscription{
 		WitnessUpdates: client.updateChan,
 		CancelSubscription: func() {
 			p.Lock()
-			defer p.Unlock()
 
 			delete(p.subscribers, clientID)
 
 			close(client.quit)
+			p.Unlock()
+
+			err := p.cancelInterceptor(inKey)
+			if err != nil {
+				srvrLog.Errorf("Cannot remove on-chain "+
+					"intercept %v: %v", inKey, err)
+			}
 		},
 	}
 
 	// Notify the htlc interceptor. There may be a client connected
 	// and willing to supply a preimage.
 	packet := &htlcswitch.InterceptedPacket{
-		Hash:           htlc.RHash,
-		IncomingExpiry: htlc.RefundTimeout,
-		IncomingAmount: htlc.Amt,
-		IncomingCircuit: models.CircuitKey{
-			ChanID: chanID,
-			HtlcID: htlc.HtlcIndex,
-		},
+		Hash:                 htlc.RHash,
+		IncomingExpiry:       htlc.RefundTimeout,
+		IncomingAmount:       htlc.Amt,
+		IncomingCircuit:      inKey,
 		OutgoingChanID:       payload.FwdInfo.NextHop,
 		OutgoingExpiry:       payload.FwdInfo.OutgoingCLTV,
 		OutgoingAmount:       payload.FwdInfo.AmountToForward,
@@ -120,6 +131,8 @@ func (p *preimageBeacon) SubscribeUpdates(
 
 	err := p.interceptor(fwd)
 	if err != nil {
+		sub.CancelSubscription()
+
 		return nil, err
 	}
 
```

### witness_beacon_test.go
```diff
@@ -1,9 +1,11 @@
 package lnd
 
 import (
+	"errors"
 	"testing"
 
 	"github.com/lightningnetwork/lnd/channeldb"
+	"github.com/lightningnetwork/lnd/graph/db/models"
 	"github.com/lightningnetwork/lnd/htlcswitch"
 	"github.com/lightningnetwork/lnd/htlcswitch/hop"
 	"github.com/lightningnetwork/lnd/lntypes"
@@ -20,9 +22,15 @@ func TestWitnessBeaconIntercept(t *testing.T) {
 
 		return nil
 	}
+	var canceledKey models.CircuitKey
+	cancelInterceptor := func(key models.CircuitKey) error {
+		canceledKey = key
+
+		return nil
+	}
 
 	p := newPreimageBeacon(
-		&mockWitnessCache{}, interceptor,
+		&mockWitnessCache{}, interceptor, cancelInterceptor,
 	)
 
 	preimage := lntypes.Preimage{1, 2, 3}
@@ -37,12 +45,56 @@ func TestWitnessBeaconIntercept(t *testing.T) {
 		[]byte{2},
 	)
 	require.NoError(t, err)
-	t.Cleanup(subscription.CancelSubscription)
 
 	require.NoError(t, interceptedFwd.Settle(preimage))
 
 	update := <-subscription.WitnessUpdates
 	require.Equal(t, preimage, update)
+
+	subscription.CancelSubscription()
+	require.Equal(t, interceptedFwd.Packet().IncomingCircuit, canceledKey)
+}
+
+// TestWitnessBeaconInterceptErrorCancels tests that a failed interceptor offer
+// tears down the witness subscription and on-chain intercept handle.
+func TestWitnessBeaconInterceptErrorCancels(t *testing.T) {
+	errInterceptor := errors.New("interceptor error")
+
+	interceptor := func(htlcswitch.InterceptedForward) error {
+		return errInterceptor
+	}
+
+	var canceledKey models.CircuitKey
+	cancelInterceptor := func(key models.CircuitKey) error {
+		canceledKey = key
+
+		return nil
+	}
+
+	p := newPreimageBeacon(
+		&mockWitnessCache{}, interceptor, cancelInterceptor,
+	)
+
+	chanID := lnwire.NewShortChanIDFromInt(1)
+	htlc := &channeldb.HTLC{
+		HtlcIndex: 2,
+		RHash:     lntypes.Hash{3},
+	}
+
+	subscription, err := p.SubscribeUpdates(
+		chanID, htlc, &hop.Payload{}, []byte{2},
+	)
+	require.ErrorIs(t, err, errInterceptor)
+	require.Nil(t, subscription)
+
+	require.Equal(t, models.CircuitKey{
+		ChanID: chanID,
+		HtlcID: htlc.HtlcIndex,
+	}, canceledKey)
+
+	p.RLock()
+	require.Empty(t, p.subscribers)
+	p.RUnlock()
 }
 
 type mockWitnessCache struct {
```
