# [?] multi: prevent nil panics in stop methods.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2024-07-27
Source: https://github.com/lightningnetwork/lnd/commit/02c1264c536f1461da7a324f95981d0eefdea76c
Type: security-commit

## Details
multi: prevent nil panics in stop methods.

With this PR we might call the stop method even when the start
method of a subsystem did not successfully finish therefore we
need to make sure we guard the stop methods for potential panics
if some variables are not initialized in the contructors of the
subsystems.

## Patch
### chainntnfs/bitcoindnotify/bitcoind.go
```diff
@@ -151,7 +151,12 @@ func (b *BitcoindNotifier) Stop() error {
 
 		close(epochClient.epochChan)
 	}
-	b.txNotifier.TearDown()
+
+	// The txNotifier is only initialized in the start method therefore we
+	// need to make sure we don't access a nil pointer here.
+	if b.txNotifier != nil {
+		b.txNotifier.TearDown()
+	}
 
 	// Stop the mempool notifier.
 	b.memNotifier.TearDown()
```

### chainntnfs/neutrinonotify/neutrino.go
```diff
@@ -152,7 +152,12 @@ func (n *NeutrinoNotifier) Stop() error {
 
 		close(epochClient.epochChan)
 	}
-	n.txNotifier.TearDown()
+
+	// The txNotifier is only initialized in the start method therefore we
+	// need to make sure we don't access a nil pointer here.
+	if n.txNotifier != nil {
+		n.txNotifier.TearDown()
+	}
 
 	return nil
 }
```

### chanfitness/chaneventstore.go
```diff
@@ -226,11 +226,17 @@ func (c *ChannelEventStore) Stop() error {
 
 	// Stop the ticker after the goroutine reading from it has exited, to
 	// avoid a race.
-	c.cfg.FlapCountTicker.Stop()
+	var err error
+	if c.cfg.FlapCountTicker == nil {
+		err = fmt.Errorf("ChannelEventStore FlapCountTicker not " +
+			"initialized")
+	} else {
+		c.cfg.FlapCountTicker.Stop()
+	}
 
 	log.Debugf("ChannelEventStore shutdown complete")
 
-	return nil
+	return err
 }
 
 // addChannel checks whether we are already tracking a channel's peer, creates a
```

### discovery/gossiper.go
```diff
@@ -753,7 +753,12 @@ func (d *AuthenticatedGossiper) stop() {
 	log.Debug("Authenticated Gossiper is stopping")
 	defer log.Debug("Authenticated Gossiper stopped")
 
-	d.blockEpochs.Cancel()
+	// `blockEpochs` is only initialized in the start routine so we make
+	// sure we don't panic here in the case where the `Stop` method is
+	// called when the `Start` method does not complete.
+	if d.blockEpochs != nil {
+		d.blockEpochs.Cancel()
+	}
 
 	d.syncMgr.Stop()
 
```

### htlcswitch/interceptable_switch.go
```diff
@@ -242,7 +242,11 @@ func (s *InterceptableSwitch) Stop() error {
 	close(s.quit)
 	s.wg.Wait()
 
-	s.blockEpochStream.Cancel()
+	// We need to check whether the start routine run and initialized the
+	// `blockEpochStream`.
+	if s.blockEpochStream != nil {
+		s.blockEpochStream.Cancel()
+	}
 
 	log.Debug("InterceptableSwitch shutdown complete")
 
```

### htlcswitch/link.go
```diff
@@ -562,14 +562,18 @@ func (l *channelLink) Stop() {
 	}
 
 	// Ensure the channel for the timer is drained.
-	if !l.updateFeeTimer.Stop() {
-		select {
-		case <-l.updateFeeTimer.C:
-		default:
+	if l.updateFeeTimer != nil {
+		if !l.updateFeeTimer.Stop() {
+			select {
+			case <-l.updateFeeTimer.C:
+			default:
+			}
 		}
 	}
 
-	l.hodlQueue.Stop()
+	if l.hodlQueue != nil {
+		l.hodlQueue.Stop()
+	}
 
 	close(l.quit)
 	l.wg.Wait()
```

### invoices/invoiceregistry.go
```diff
@@ -261,15 +261,21 @@ func (i *InvoiceRegistry) Stop() error {
 	log.Info("InvoiceRegistry shutting down...")
 	defer log.Debug("InvoiceRegistry shutdown complete")
 
-	i.expiryWatcher.Stop()
+	var err error
+	if i.expiryWatcher == nil {
+		err = fmt.Errorf("InvoiceRegistry expiryWatcher is not " +
+			"initialized")
+	} else {
+		i.expiryWatcher.Stop()
+	}
 
 	close(i.quit)
 
 	i.wg.Wait()
 
 	log.Debug("InvoiceRegistry shutdown complete")
 
-	return nil
+	return err
 }
 
 // invoiceEvent represents a new event that has modified on invoice on disk.
```

### lnwallet/chainfee/estimator.go
```diff
@@ -884,7 +884,9 @@ func (w *WebAPIEstimator) Stop() error {
 		return nil
 	}
 
-	w.updateFeeTicker.Stop()
+	if w.updateFeeTicker != nil {
+		w.updateFeeTicker.Stop()
+	}
 
 	close(w.quit)
 	w.wg.Wait()
```

### server.go
```diff
@@ -2105,6 +2105,9 @@ func (s *server) Start() error {
 			}
 		}
 
+		// chanSubSwapper must be started after the `channelNotifier`
+		// because it depends on channel events as a synchronization
+		// point.
 		cleanup = cleanup.add(s.chanSubSwapper.Stop)
 		if err := s.chanSubSwapper.Start(); err != nil {
 			startErr = err
```

### tor/controller.go
```diff
@@ -186,6 +186,10 @@ func (c *Controller) Stop() error {
 	// Reset service ID.
 	c.activeServiceID = ""
 
+	if c.conn == nil {
+		return fmt.Errorf("no connection available to the tor server")
+	}
+
 	return c.conn.Close()
 }
 
```
