# [?] fix race condition causing TestAutoNATServiceDialError test failure (#1312)

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2022-02-06
Source: https://github.com/libp2p/go-libp2p/commit/807e6b079ad26ec9823d95d74f00a347ef40221e
Type: security-commit

## Details
fix race condition causing TestAutoNATServiceDialError test failure (#1312)

## Patch
### p2p/host/autonat/svc.go
```diff
@@ -242,6 +242,7 @@ func (as *autoNATService) Enable() {
 	ctx, cancel := context.WithCancel(context.Background())
 	as.instance = cancel
 	as.backgroundRunning = make(chan struct{})
+	as.config.host.SetStreamHandler(AutoNATProto, as.handleStream)
 
 	go as.background(ctx)
 }
@@ -251,6 +252,7 @@ func (as *autoNATService) Disable() {
 	as.instanceLock.Lock()
 	defer as.instanceLock.Unlock()
 	if as.instance != nil {
+		as.config.host.RemoveStreamHandler(AutoNATProto)
 		as.instance()
 		as.instance = nil
 		<-as.backgroundRunning
@@ -259,7 +261,6 @@ func (as *autoNATService) Disable() {
 
 func (as *autoNATService) background(ctx context.Context) {
 	defer close(as.backgroundRunning)
-	as.config.host.SetStreamHandler(AutoNATProto, as.handleStream)
 
 	timer := time.NewTimer(as.config.throttleResetPeriod)
 	defer timer.Stop()
@@ -274,7 +275,6 @@ func (as *autoNATService) background(ctx context.Context) {
 			jitter := rand.Float32() * float32(as.config.throttleResetJitter)
 			timer.Reset(as.config.throttleResetPeriod + time.Duration(int64(jitter)))
 		case <-ctx.Done():
-			as.config.host.RemoveStreamHandler(AutoNATProto)
 			return
 		}
 	}
```
