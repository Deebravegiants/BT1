# [?] [FAB-18333] Fix panic in cluster/comm#TestRenewCertificates

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2020-11-10
Source: https://github.com/hyperledger/fabric/commit/f1058a802cd6070ecb3e0aaf17793b8655940f70
Type: security-commit

## Details
[FAB-18333] Fix panic in cluster/comm#TestRenewCertificates

In the unit test TestRenewCertificates, node 2 is restarted and its certificates
are rotated.

It is tested that node 1 fails to re-connect to the old certificate until it is reconfigued.
However, since it is not aware of the new reconfiguration, the old gRPC stream might be stale
and it might not be detected, and the expected error that is checked results in a nil pointer panic.

This PR aims to fix the nil pointer panic, by repeatedly trying to use the stream until an error is returned.
This ensures that the gRPC stream is un-usable and when the server starts with a new certificate
it will still be un-usable.

Change-Id: I038624907ebab198bb3a193b137a47b2e7c970d0
Signed-off-by: Yacov Manevich <yacovm@il.ibm.com>

## Patch
### orderer/common/cluster/comm_test.go
```diff
@@ -197,11 +197,6 @@ func (cn *clusterNode) stop() {
 }
 
 func (cn *clusterNode) renewCertificates() {
-	// Stop the gRPC service
-	cn.srv.Stop()
-	// and restart it afterwards
-	defer cn.resurrect()
-
 	clientKeyPair, err := ca.NewClientCertKeyPair()
 	if err != nil {
 		panic(fmt.Errorf("failed creating client certificate %v", err))
@@ -878,9 +873,33 @@ func TestRenewCertificates(t *testing.T) {
 
 	// Close outgoing connections from node2 to node1
 	node2.c.Configure(testChannel, nil)
+	// Stop the gRPC service of node 2 to replace its certificate
+	node2.srv.Stop()
+
+	// Wait until node 1 detects this
+	gt := gomega.NewGomegaWithT(t)
+	gt.Eventually(func() error {
+		remote, err := node1.c.Remote(testChannel, node2.nodeInfo.ID)
+		if err != nil {
+			return err
+		}
+		stream, err := remote.NewStream(time.Hour)
+		if err != nil {
+			return err
+		}
+		err = stream.Send(wrapSubmitReq(testSubReq))
+		if err != nil {
+			return err
+		}
+		return nil
+	}).Should(gomega.Not(gomega.Succeed()))
+
 	// Renew node 2's keys
 	node2.renewCertificates()
 
+	// Resurrect node 2 to make it service connections again
+	node2.resurrect()
+
 	// W.L.O.G, try to send a message from node1 to node2
 	// It should fail, because node2's server certificate has now changed,
 	// so it closed the connection to the remote node
```
