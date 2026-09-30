# [?] Fix data race in gossip/discovery test

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2020-09-10
Source: https://github.com/hyperledger/fabric/commit/65d0b62479ad80da77a5e01ae8c152751b38f0ce
Type: security-commit

## Details
Fix data race in gossip/discovery test

This change set fixes two data races:

1) A logger reference was overriden while the logger might be in use.
   I changed the implementation so that the logger will be injected.

2) A shared number was incremented by logger hooks that are instantiated
   multiple times for different peers.
   I made it so that each logger hook receives its own counter, which is
   no longer a counter but a map of log entries that are searched.

Change-Id: Ic69f604f30a16e1a1fb9050ba9145dfa38e05146
Signed-off-by: yacovm <yacovm@il.ibm.com>

## Patch
### gossip/discovery/discovery_impl.go
```diff
@@ -86,7 +86,7 @@ type DiscoveryConfig struct {
 
 // NewDiscoveryService returns a new discovery service with the comm module passed and the crypto service passed
 func NewDiscoveryService(self NetworkMember, comm CommService, crypt CryptoService, disPol DisclosurePolicy,
-	config DiscoveryConfig, anchorPeerTracker AnchorPeerTracker) Discovery {
+	config DiscoveryConfig, anchorPeerTracker AnchorPeerTracker, logger util.Logger) Discovery {
 	d := &gossipDiscoveryImpl{
 		self:             self,
 		incTime:          uint64(time.Now().UnixNano()),
@@ -100,7 +100,7 @@ func NewDiscoveryService(self NetworkMember, comm CommService, crypt CryptoServi
 		comm:             comm,
 		lock:             &sync.RWMutex{},
 		toDieChan:        make(chan struct{}),
-		logger:           util.GetLogger(util.DiscoveryLogger, self.InternalEndpoint),
+		logger:           logger,
 		disclosurePolicy: disPol,
 		pubsub:           util.NewPubSub(),
 
```

### gossip/discovery/discovery_test.go
```diff
@@ -391,11 +391,11 @@ func createDiscoveryInstanceThatGossips(port int, id string, bootstrapPeers []st
 
 func createDiscoveryInstanceThatGossipsWithInterceptors(port int, id string, bootstrapPeers []string, shouldGossip bool, pol DisclosurePolicy, f func(*protoext.SignedGossipMessage), config DiscoveryConfig) *gossipInstance {
 	mockTracker := &mockAnchorPeerTracker{}
-	return createDiscoveryInstanceWithAnchorPeerTracker(port, id, bootstrapPeers, shouldGossip, pol, f, config, mockTracker)
+	return createDiscoveryInstanceWithAnchorPeerTracker(port, id, bootstrapPeers, shouldGossip, pol, f, config, mockTracker, nil)
 }
 
 func createDiscoveryInstanceWithAnchorPeerTracker(port int, id string, bootstrapPeers []string, shouldGossip bool, pol DisclosurePolicy,
-	f func(*protoext.SignedGossipMessage), config DiscoveryConfig, anchorPeerTracker AnchorPeerTracker) *gossipInstance {
+	f func(*protoext.SignedGossipMessage), config DiscoveryConfig, anchorPeerTracker AnchorPeerTracker, logger util.Logger) *gossipInstance {
 	comm := &dummyCommModule{
 		conns:          make(map[string]*grpc.ClientConn),
 		streams:        make(map[string]proto.Gossip_GossipStreamClient),
@@ -428,7 +428,10 @@ func createDiscoveryInstanceWithAnchorPeerTracker(port int, id string, bootstrap
 
 	config.BootstrapPeers = bootstrapPeers
 
-	discSvc := NewDiscoveryService(self, comm, comm, pol, config, anchorPeerTracker)
+	if logger == nil {
+		logger = util.GetLogger(util.DiscoveryLogger, self.InternalEndpoint)
+	}
+	discSvc := NewDiscoveryService(self, comm, comm, pol, config, anchorPeerTracker, logger)
 	for _, bootPeer := range bootstrapPeers {
 		bp := bootPeer
 		discSvc.Connect(NetworkMember{Endpoint: bp, InternalEndpoint: bootPeer}, func() (*PeerIdentification, error) {
@@ -1725,39 +1728,50 @@ func TestMembershipAfterExpiration(t *testing.T) {
 	var inst *gossipInstance
 	mockTracker := &mockAnchorPeerTracker{[]string{anchorPeer}}
 
-	// use a custom logger to verify messages from expiration callback
-	expectedMsgs := []string{
-		"Do not remove bootstrap or anchor peer endpoint localhost:9120 from membership",
-		"Removing member: Endpoint: localhost:9121",
-	}
-	numMsgsFound := 0
 	l, err := zap.NewDevelopment()
-	require.NoError(t, err)
-	expired := make(chan struct{})
-	logger := flogging.NewFabricLogger(l, zap.Hooks(func(entry zapcore.Entry) error {
-		// do nothing if we already found all the expectedMsgs
-		if numMsgsFound == len(expectedMsgs) {
-			return nil
+	assert.NoError(t, err)
+	expired := make(chan struct{}, 1)
+
+	// use a custom logger to verify messages from expiration callback
+	loggerThatTracksCustomMessage := func() util.Logger {
+		var lock sync.RWMutex
+		expectedMsgs := map[string]struct{}{
+			"Do not remove bootstrap or anchor peer endpoint localhost:9120 from membership":                                   {},
+			"Removing member: Endpoint: localhost:9121, InternalEndpoint: localhost:9121, PKIID: 6c6f63616c686f73743a39313231": {},
 		}
-		for _, msg := range expectedMsgs {
-			if strings.Contains(entry.Message, msg) {
-				numMsgsFound++
-				if numMsgsFound == len(expectedMsgs) {
-					expired <- struct{}{}
+
+		return flogging.NewFabricLogger(l, zap.Hooks(func(entry zapcore.Entry) error {
+			// do nothing if we already found all the expectedMsgs
+			lock.RLock()
+			expectedMsgSize := len(expectedMsgs)
+			lock.RUnlock()
+
+			if expectedMsgSize == 0 {
+				select {
+				case expired <- struct{}{}:
+				default:
+					// no room is fine, continue
 				}
-				break
+				return nil
 			}
-		}
-		return nil
-	}))
+
+			lock.Lock()
+			defer lock.Unlock()
+
+			if _, matched := expectedMsgs[entry.Message]; matched {
+				delete(expectedMsgs, entry.Message)
+			}
+			return nil
+		}))
+	}
 
 	// Start all peers, connect to the anchor peer and verify full membership
 	for i := 0; i < peersNum; i++ {
 		id := fmt.Sprintf("d%d", i)
-		inst = createDiscoveryInstanceWithAnchorPeerTracker(ports[i], id, bootPeers, true, noopPolicy, func(_ *protoext.SignedGossipMessage) {}, config, mockTracker)
+		logger := loggerThatTracksCustomMessage()
+		inst = createDiscoveryInstanceWithAnchorPeerTracker(ports[i], id, bootPeers, true, noopPolicy, func(_ *protoext.SignedGossipMessage) {}, config, mockTracker, logger)
 		instances = append(instances, inst)
 	}
-	instances[peersNum-1].Discovery.(*gossipDiscoveryImpl).logger = logger
 	for i := 1; i < peersNum; i++ {
 		connect(instances[i], anchorPeer)
 	}
@@ -1783,7 +1797,7 @@ func TestMembershipAfterExpiration(t *testing.T) {
 	// Especially, we want to test that peer2 won't be isolated
 	for i := 0; i < peersNum-1; i++ {
 		id := fmt.Sprintf("d%d", i)
-		inst = createDiscoveryInstanceWithAnchorPeerTracker(ports[i], id, bootPeers, true, noopPolicy, func(_ *protoext.SignedGossipMessage) {}, config, mockTracker)
+		inst = createDiscoveryInstanceWithAnchorPeerTracker(ports[i], id, bootPeers, true, noopPolicy, func(_ *protoext.SignedGossipMessage) {}, config, mockTracker, nil)
 		instances[i] = inst
 	}
 	connect(instances[1], anchorPeer)
```

### gossip/gossip/gossip_impl.go
```diff
@@ -131,8 +131,10 @@ func New(conf *Config, s *grpc.Server, sa api.SecurityAdvisor,
 		MsgExpirationFactor:          conf.MsgExpirationFactor,
 		BootstrapPeers:               conf.BootstrapPeers,
 	}
-	g.disc = discovery.NewDiscoveryService(g.selfNetworkMember(), g.discAdapter, g.disSecAdap, g.disclosurePolicy,
-		discoveryConfig, anchorPeerTracker)
+	self := g.selfNetworkMember()
+	logger := util.GetLogger(util.DiscoveryLogger, self.InternalEndpoint)
+	g.disc = discovery.NewDiscoveryService(self, g.discAdapter, g.disSecAdap, g.disclosurePolicy,
+		discoveryConfig, anchorPeerTracker, logger)
 	g.logger.Infof("Creating gossip service with self membership of %s", g.selfNetworkMember())
 
 	g.certPuller = g.createCertStorePuller()
```
