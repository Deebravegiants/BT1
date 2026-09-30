# [?] swarm/pss: fixing race condition (#18487)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-01-21
Source: https://github.com/celo-org/celo-blockchain/commit/105008b6a121ade656bf63125cecb467e2434d95
Type: security-commit

## Details
swarm/pss: fixing race condition (#18487)

## Patch
### swarm/pss/pss.go
```diff
@@ -340,6 +340,7 @@ func (p *Pss) Register(topic *Topic, hndlr *handler) func() {
 	}
 	return func() { p.deregister(topic, hndlr) }
 }
+
 func (p *Pss) deregister(topic *Topic, hndlr *handler) {
 	p.handlersMu.Lock()
 	defer p.handlersMu.Unlock()
@@ -362,13 +363,6 @@ func (p *Pss) deregister(topic *Topic, hndlr *handler) {
 	delete(handlers, hndlr)
 }
 
-// get all registered handlers for respective topics
-func (p *Pss) getHandlers(topic Topic) map[*handler]bool {
-	p.handlersMu.RLock()
-	defer p.handlersMu.RUnlock()
-	return p.handlers[topic]
-}
-
 // Filters incoming messages for processing or forwarding.
 // Check if address partially matches
 // If yes, it CAN be for us, and we process it
@@ -427,7 +421,6 @@ func (p *Pss) handlePssMsg(ctx context.Context, msg interface{}) error {
 		}
 	}
 	return nil
-
 }
 
 // Entry point to processing a message for which the current node can be the intended recipient.
@@ -472,13 +465,22 @@ func (p *Pss) process(pssmsg *PssMsg, raw bool, prox bool) error {
 	p.executeHandlers(psstopic, payload, from, raw, prox, asymmetric, keyid)
 
 	return nil
+}
 
+// copy all registered handlers for respective topic in order to avoid data race or deadlock
+func (p *Pss) getHandlers(topic Topic) (ret []*handler) {
+	p.handlersMu.RLock()
+	defer p.handlersMu.RUnlock()
+	for k := range p.handlers[topic] {
+		ret = append(ret, k)
+	}
+	return ret
 }
 
 func (p *Pss) executeHandlers(topic Topic, payload []byte, from PssAddress, raw bool, prox bool, asymmetric bool, keyid string) {
 	handlers := p.getHandlers(topic)
 	peer := p2p.NewPeer(enode.ID{}, fmt.Sprintf("%x", from), []p2p.Cap{})
-	for h := range handlers {
+	for _, h := range handlers {
 		if !h.caps.raw && raw {
 			log.Warn("norawhandler")
 			continue
```
