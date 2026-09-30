# [?] Fix data race in price-feeder websocket controller (#2256)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2025-07-23
Source: https://github.com/sei-protocol/sei-chain/commit/85928961bebfa600796264c0b7acaa38dbacd2c7
Type: security-commit

## Details
Fix data race in price-feeder websocket controller (#2256)

fix race

## Patch
### oracle/price-feeder/oracle/provider/ws_controller.go
```diff
@@ -92,7 +92,13 @@ func (wsc *WebsocketController) Start() {
 		go wsc.readWebSocket()
 		go wsc.pingLoop()
 
-		if err := wsc.subscribe(wsc.subscriptionMsgs); err != nil {
+		// Safely read subscriptionMsgs with mutex protection
+		wsc.mtx.Lock()
+		subscriptionMsgsCopy := make([]interface{}, len(wsc.subscriptionMsgs))
+		copy(subscriptionMsgsCopy, wsc.subscriptionMsgs)
+		wsc.mtx.Unlock()
+
+		if err := wsc.subscribe(subscriptionMsgsCopy); err != nil {
 			wsc.logger.Err(err).Send()
 			wsc.close()
 			continue
@@ -147,7 +153,12 @@ func (wsc *WebsocketController) AddSubscriptionMsgs(msgs []interface{}) error {
 	if err != nil {
 		return err
 	}
+
+	// Safely write to subscriptionMsgs with mutex protection
+	wsc.mtx.Lock()
 	wsc.subscriptionMsgs = append(wsc.subscriptionMsgs, msgs...)
+	wsc.mtx.Unlock()
+
 	return nil
 }
 
```
