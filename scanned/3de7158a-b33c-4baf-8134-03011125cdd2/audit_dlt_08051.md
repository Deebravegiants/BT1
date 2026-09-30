# [?] swarm/pss: fix data race on topicHandlerCaps map (#18523)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-01-25
Source: https://github.com/celo-org/celo-blockchain/commit/2209fede4e2cb19bc6336562fc41812ec1d56435
Type: security-commit

## Details
swarm/pss: fix data race on topicHandlerCaps map (#18523)

## Patch
### swarm/pss/pss.go
```diff
@@ -138,10 +138,11 @@ type Pss struct {
 	symKeyDecryptCacheCapacity int       // max amount of symkeys to keep.
 
 	// message handling
-	handlers         map[Topic]map[*handler]bool // topic and version based pss payload handlers. See pss.Handle()
-	handlersMu       sync.RWMutex
-	hashPool         sync.Pool
-	topicHandlerCaps map[Topic]*handlerCaps // caches capabilities of each topic's handlers (see handlerCap* consts in types.go)
+	handlers           map[Topic]map[*handler]bool // topic and version based pss payload handlers. See pss.Handle()
+	handlersMu         sync.RWMutex
+	hashPool           sync.Pool
+	topicHandlerCaps   map[Topic]*handlerCaps // caches capabilities of each topic's handlers
+	topicHandlerCapsMu sync.RWMutex
 
 	// process
 	quitC chan struct{}
@@ -307,6 +308,19 @@ func (p *Pss) PublicKey() *ecdsa.PublicKey {
 // SECTION: Message handling
 /////////////////////////////////////////////////////////////////////
 
+func (p *Pss) getTopicHandlerCaps(topic Topic) (hc *handlerCaps, found bool) {
+	p.topicHandlerCapsMu.RLock()
+	defer p.topicHandlerCapsMu.RUnlock()
+	hc, found = p.topicHandlerCaps[topic]
+	return
+}
+
+func (p *Pss) setTopicHandlerCaps(topic Topic, hc *handlerCaps) {
+	p.topicHandlerCapsMu.Lock()
+	defer p.topicHandlerCapsMu.Unlock()
+	p.topicHandlerCaps[topic] = hc
+}
+
 // Links a handler function to a Topic
 //
 // All incoming messages with an envelope Topic matching the
@@ -323,20 +337,24 @@ func (p *Pss) Register(topic *Topic, hndlr *handler) func() {
 	if handlers == nil {
 		handlers = make(map[*handler]bool)
 		p.handlers[*topic] = handlers
-		log.Debug("registered handler", "caps", hndlr.caps)
+		log.Debug("registered handler", "capabilities", hndlr.caps)
 	}
 	if hndlr.caps == nil {
 		hndlr.caps = &handlerCaps{}
 	}
 	handlers[hndlr] = true
-	if _, ok := p.topicHandlerCaps[*topic]; !ok {
-		p.topicHandlerCaps[*topic] = &handlerCaps{}
+
+	capabilities, ok := p.getTopicHandlerCaps(*topic)
+	if !ok {
+		capabilities = &handlerCaps{}
+		p.setTopicHandlerCaps(*topic, capabilities)
 	}
+
 	if hndlr.caps.raw {
-		p.topicHandlerCaps[*topic].raw = true
+		capabilities.raw = true
 	}
 	if hndlr.caps.prox {
-		p.topicHandlerCaps[*topic].prox = true
+		capabilities.prox = true
 	}
 	return func() { p.deregister(topic, hndlr) }
 }
@@ -357,7 +375,7 @@ func (p *Pss) deregister(topic *Topic, hndlr *handler) {
 				caps.prox = true
 			}
 		}
-		p.topicHandlerCaps[*topic] = caps
+		p.setTopicHandlerCaps(*topic, caps)
 		return
 	}
 	delete(handlers, hndlr)
@@ -390,8 +408,8 @@ func (p *Pss) handlePssMsg(ctx context.Context, msg interface{}) error {
 	// raw is simplest handler contingency to check, so check that first
 	var isRaw bool
 	if pssmsg.isRaw() {
-		if _, ok := p.topicHandlerCaps[psstopic]; ok {
-			if !p.topicHandlerCaps[psstopic].raw {
+		if capabilities, ok := p.getTopicHandlerCaps(psstopic); ok {
+			if !capabilities.raw {
 				log.Debug("No handler for raw message", "topic", psstopic)
 				return nil
 			}
@@ -404,8 +422,8 @@ func (p *Pss) handlePssMsg(ctx context.Context, msg interface{}) error {
 	// - prox handler on message and we are in prox regardless of partial address match
 	// store this result so we don't calculate again on every handler
 	var isProx bool
-	if _, ok := p.topicHandlerCaps[psstopic]; ok {
-		isProx = p.topicHandlerCaps[psstopic].prox
+	if capabilities, ok := p.getTopicHandlerCaps(psstopic); ok {
+		isProx = capabilities.prox
 	}
 	isRecipient := p.isSelfPossibleRecipient(pssmsg, isProx)
 	if !isRecipient {
@@ -783,8 +801,8 @@ func (p *Pss) SendRaw(address PssAddress, topic Topic, msg []byte) error {
 
 	// if we have a proxhandler on this topic
 	// also deliver message to ourselves
-	if _, ok := p.topicHandlerCaps[topic]; ok {
-		if p.isSelfPossibleRecipient(pssMsg, true) && p.topicHandlerCaps[topic].prox {
+	if capabilities, ok := p.getTopicHandlerCaps(topic); ok {
+		if p.isSelfPossibleRecipient(pssMsg, true) && capabilities.prox {
 			return p.process(pssMsg, true, true)
 		}
 	}
@@ -885,8 +903,8 @@ func (p *Pss) send(to []byte, topic Topic, msg []byte, asymmetric bool, key []by
 	if err != nil {
 		return err
 	}
-	if _, ok := p.topicHandlerCaps[topic]; ok {
-		if p.isSelfPossibleRecipient(pssMsg, true) && p.topicHandlerCaps[topic].prox {
+	if capabilities, ok := p.getTopicHandlerCaps(topic); ok {
+		if p.isSelfPossibleRecipient(pssMsg, true) && capabilities.prox {
 			return p.process(pssMsg, true, true)
 		}
 	}
```
