# [?] fix another data race in dispatcher (#438)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2019-01-09
Source: https://github.com/iotexproject/iotex-core/commit/f9f8f7fbae9179767155c9a402855ce3944664d8
Type: security-commit

## Details
fix another data race in dispatcher (#438)

* fix another data race

## Patch
### dispatcher/dispatcher.go
```diff
@@ -288,13 +288,16 @@ func (d *IotxDispatcher) HandleBroadcast(chainID uint32, message proto.Message)
 			Str("error", err.Error()).
 			Msg("unexpected message handled by HandleBroadcast")
 	}
+	d.subscribersMU.RLock()
 	subscriber, ok := d.subscribers[chainID]
 	if !ok {
 		logger.Warn().
 			Uint32("chainID", chainID).
 			Msg("chainID has not been registered in dispatcher")
+		d.subscribersMU.RUnlock()
 		return
 	}
+	d.subscribersMU.RUnlock()
 
 	switch msgType {
 	case pb.MsgConsensusType:
```
