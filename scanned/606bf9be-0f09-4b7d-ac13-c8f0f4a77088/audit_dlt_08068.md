# [?] les: fix server panic when discovery disabled (#16055)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2018-02-10
Source: https://github.com/celo-org/celo-blockchain/commit/2f849ade8204a4b417202d90c66e2f5bef4e965d
Type: security-commit

## Details
les: fix server panic when discovery disabled (#16055)

## Patch
### les/server.go
```diff
@@ -111,15 +111,17 @@ func (s *LesServer) Protocols() []p2p.Protocol {
 // Start starts the LES server
 func (s *LesServer) Start(srvr *p2p.Server) {
 	s.protocolManager.Start(s.config.LightPeers)
-	for _, topic := range s.lesTopics {
-		topic := topic
-		go func() {
-			logger := log.New("topic", topic)
-			logger.Info("Starting topic registration")
-			defer logger.Info("Terminated topic registration")
-
-			srvr.DiscV5.RegisterTopic(topic, s.quitSync)
-		}()
+	if srvr.DiscV5 != nil {
+		for _, topic := range s.lesTopics {
+			topic := topic
+			go func() {
+				logger := log.New("topic", topic)
+				logger.Info("Starting topic registration")
+				defer logger.Info("Terminated topic registration")
+
+				srvr.DiscV5.RegisterTopic(topic, s.quitSync)
+			}()
+		}
 	}
 	s.privateKey = srvr.PrivateKey
 	s.protocolManager.blockLoop()
```
