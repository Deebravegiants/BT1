# [?] [actsync] Fix data race (#4456)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2024-11-28
Source: https://github.com/iotexproject/iotex-core/commit/5b64c2b02eb9ae57980f6d05634a11adcb3adf6d
Type: security-commit

## Details
[actsync] Fix data race (#4456)

## Patch
### actsync/actionsync.go
```diff
@@ -95,7 +95,6 @@ func (as *ActionSync) Stop(ctx context.Context) error {
 		return err
 	}
 	close(as.quit)
-	close(as.syncChan)
 	as.wg.Wait()
 	return nil
 }
@@ -127,28 +126,33 @@ func (as *ActionSync) ReceiveAction(_ context.Context, hash hash.Hash256) {
 
 func (as *ActionSync) sync() {
 	defer as.wg.Done()
-	for hash := range as.syncChan {
-		log.L().Debug("syncing action", log.Hex("hash", hash[:]))
-		channelFullnessMtc.WithLabelValues("action").Set(float64(len(as.syncChan)) / float64(cap(as.syncChan)))
-		ctx, cancel := context.WithTimeout(context.Background(), unicaseTimeout)
-		defer cancel()
-		msg, ok := as.actions.Load(hash)
-		if !ok {
-			log.L().Debug("action not requested or already received", log.Hex("hash", hash[:]))
-			continue
-		}
-		if time.Since(msg.(*actionMsg).lastTime) < as.cfg.Interval {
-			log.L().Debug("action is recently requested", log.Hex("hash", hash[:]))
-			continue
-		}
-		msg.(*actionMsg).lastTime = time.Now()
-		// TODO: enhancement, request multiple actions in one message
-		if err := as.requestFromNeighbors(ctx, hash); err != nil {
-			log.L().Warn("Failed to request action from neighbors", zap.Error(err))
-			counterMtc.WithLabelValues("failed").Inc()
+	for {
+		select {
+		case hash := <-as.syncChan:
+			log.L().Debug("syncing action", log.Hex("hash", hash[:]))
+			channelFullnessMtc.WithLabelValues("action").Set(float64(len(as.syncChan)) / float64(cap(as.syncChan)))
+			ctx, cancel := context.WithTimeout(context.Background(), unicaseTimeout)
+			defer cancel()
+			msg, ok := as.actions.Load(hash)
+			if !ok {
+				log.L().Debug("action not requested or already received", log.Hex("hash", hash[:]))
+				continue
+			}
+			if time.Since(msg.(*actionMsg).lastTime) < as.cfg.Interval {
+				log.L().Debug("action is recently requested", log.Hex("hash", hash[:]))
+				continue
+			}
+			msg.(*actionMsg).lastTime = time.Now()
+			// TODO: enhancement, request multiple actions in one message
+			if err := as.requestFromNeighbors(ctx, hash); err != nil {
+				log.L().Warn("Failed to request action from neighbors", zap.Error(err))
+				counterMtc.WithLabelValues("failed").Inc()
+			}
+		case <-as.quit:
+			log.L().Info("quitting action sync")
+			return
 		}
 	}
-	log.L().Info("quitting action sync")
 }
 
 func (as *ActionSync) triggerSync() {
```

### actsync/actionsync_test.go
```diff
@@ -126,4 +126,40 @@ func TestActionSync(t *testing.T) {
 			r.False(ok, "action should be removed after received")
 		}
 	})
+	t.Run("requestWhenStopping", func(t *testing.T) {
+		count := atomic.Int32{}
+		as := NewActionSync(Config{
+			Size:     1000,
+			Interval: 10 * time.Millisecond,
+		}, &Helper{
+			P2PNeighbor: func() ([]peer.AddrInfo, error) {
+				return neighbors, nil
+			},
+			UnicastOutbound: func(_ context.Context, p peer.AddrInfo, msg proto.Message) error {
+				count.Add(1)
+				return nil
+			},
+		})
+		r.NoError(as.Start(context.Background()))
+		acts := []hash.Hash256{}
+		for i := 0; i < 100; i++ {
+			acts = append(acts, hash.Hash256b([]byte{byte(i)}))
+		}
+		wg := sync.WaitGroup{}
+		for i := 0; i < 10; i++ {
+			wg.Add(1)
+			go func(i int) {
+				defer wg.Done()
+				for k := 0; k <= 10; k++ {
+					idx := i*10 + k
+					if idx >= len(acts) {
+						break
+					}
+					as.RequestAction(context.Background(), acts[idx])
+				}
+			}(i)
+		}
+		r.NoError(as.Stop(context.Background()))
+		wg.Wait()
+	})
 }
```
