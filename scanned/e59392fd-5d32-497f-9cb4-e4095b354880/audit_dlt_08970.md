# [?] Fix data race in expiration UT (#847)

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2020-03-12
Source: https://github.com/hyperledger/fabric/commit/ff29da2ddccd855a1d60259da6068268b43f2945
Type: security-commit

## Details
Fix data race in expiration UT (#847)

Change-Id: I341dcfdc1b5138b77ced6283ee6ef1fba7f8d64d
Signed-off-by: yacovm <yacovm@il.ibm.com>

## Patch
### gossip/gossip/gossip_test.go
```diff
@@ -54,8 +54,6 @@ var discoveryConfig = discovery.DiscoveryConfig{
 	ReconnectInterval:            aliveTimeInterval,
 }
 
-var expirationTimes = map[string]time.Time{}
-
 var orgInChannelA = api.OrgIdentityType("ORG1")
 
 func acceptData(m interface{}) bool {
@@ -109,6 +107,7 @@ type naiveCryptoService struct {
 	allowedPkiIDS       map[string]struct{}
 	revokedPkiIDS       map[string]struct{}
 	expirationTimesLock *sync.RWMutex
+	expirationTimes     map[string]time.Time
 }
 
 func (cs *naiveCryptoService) OrgByPeerIdentity(api.PeerIdentityType) api.OrgIdentityType {
@@ -120,7 +119,7 @@ func (cs *naiveCryptoService) Expiration(peerIdentity api.PeerIdentityType) (tim
 		cs.expirationTimesLock.RLock()
 		defer cs.expirationTimesLock.RUnlock()
 	}
-	if exp, exists := expirationTimes[string(peerIdentity)]; exists {
+	if exp, exists := cs.expirationTimes[string(peerIdentity)]; exists {
 		return exp, nil
 	}
 	return time.Now().Add(time.Hour), nil
@@ -262,10 +261,10 @@ func newGossipInstanceWithGRPC(id int, port int, gRPCServer *corecomm.GRPCServer
 	return newGossipInstanceWithGrpcMcsMetrics(id, port, gRPCServer, certs, secureDialOpts, maxMsgCount, mcs, metrics, bootPorts...)
 }
 
-func newGossipInstanceWithGRPCWithLock(lock *sync.RWMutex, id int, port int, gRPCServer *corecomm.GRPCServer, certs *common.TLSCertificates,
+func newGossipInstanceWithExpiration(expirations map[string]time.Time, lock *sync.RWMutex, id int, port int, gRPCServer *corecomm.GRPCServer, certs *common.TLSCertificates,
 	secureDialOpts api.PeerSecureDialOpts, maxMsgCount int, bootPorts ...int) *gossipGRPC {
 	metrics := metrics.NewGossipMetrics(&disabled.Provider{})
-	mcs := &naiveCryptoService{expirationTimesLock: lock}
+	mcs := &naiveCryptoService{expirationTimesLock: lock, expirationTimes: expirations}
 	return newGossipInstanceWithGrpcMcsMetrics(id, port, gRPCServer, certs, secureDialOpts, maxMsgCount, mcs, metrics, bootPorts...)
 }
 
@@ -1401,17 +1400,18 @@ func TestIdentityExpiration(t *testing.T) {
 	// the revoked peer at all because its identity would seem to them as expired
 
 	var expirationTimesLock sync.RWMutex
+	expirationTimes := map[string]time.Time{}
 
 	port1, grpc1, certs1, secDialOpts1, _ := util.CreateGRPCLayer()
-	g1 := newGossipInstanceWithGRPCWithLock(&expirationTimesLock, 1, port1, grpc1, certs1, secDialOpts1, 100)
+	g1 := newGossipInstanceWithExpiration(expirationTimes, &expirationTimesLock, 1, port1, grpc1, certs1, secDialOpts1, 100)
 	port2, grpc2, certs2, secDialOpts2, _ := util.CreateGRPCLayer()
-	g2 := newGossipInstanceWithGRPCWithLock(&expirationTimesLock, 2, port2, grpc2, certs2, secDialOpts2, 100, port1)
+	g2 := newGossipInstanceWithExpiration(expirationTimes, &expirationTimesLock, 2, port2, grpc2, certs2, secDialOpts2, 100, port1)
 	port3, grpc3, certs3, secDialOpts3, _ := util.CreateGRPCLayer()
-	g3 := newGossipInstanceWithGRPCWithLock(&expirationTimesLock, 3, port3, grpc3, certs3, secDialOpts3, 100, port1)
+	g3 := newGossipInstanceWithExpiration(expirationTimes, &expirationTimesLock, 3, port3, grpc3, certs3, secDialOpts3, 100, port1)
 	port4, grpc4, certs4, secDialOpts4, _ := util.CreateGRPCLayer()
-	g4 := newGossipInstanceWithGRPCWithLock(&expirationTimesLock, 4, port4, grpc4, certs4, secDialOpts4, 100, port1)
+	g4 := newGossipInstanceWithExpiration(expirationTimes, &expirationTimesLock, 4, port4, grpc4, certs4, secDialOpts4, 100, port1)
 	port5, grpc5, certs5, secDialOpts5, _ := util.CreateGRPCLayer()
-	g5 := newGossipInstanceWithGRPCWithLock(&expirationTimesLock, 5, port5, grpc5, certs5, secDialOpts5, 100, port1)
+	g5 := newGossipInstanceWithExpiration(expirationTimes, &expirationTimesLock, 5, port5, grpc5, certs5, secDialOpts5, 100, port1)
 
 	// Set expiration of the last peer to 5 seconds from now
 	endpointLast := fmt.Sprintf("127.0.0.1:%d", port5)
```
