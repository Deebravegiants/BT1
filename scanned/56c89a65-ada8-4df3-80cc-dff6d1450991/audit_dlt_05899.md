# [?] [FAB-18329] Fix data race in cluster/comm_test#TestRenewCertificates (#2089)

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2020-11-09
Source: https://github.com/hyperledger/fabric/commit/901fe6ceccf0d85ed25cc62ad32a3fd65131800f
Type: security-commit

## Details
[FAB-18329] Fix data race in cluster/comm_test#TestRenewCertificates (#2089)

This commit fixes a data race in orderer/common/cluster/comm_test.go#TestRenewCertificates.

The race occurred because the TLS configuration was updated from the test goroutine,
while a gRPC connection was being established from another goroutine, and as a result,
the TLS configuration was loaded without memory synchronization with the first goroutine.

I made the test close the gRPC connections before reconfiguring the communication layer.

Change-Id: I82b9cc685e9160e480ce77ec7e0a233b106eb0e5
Signed-off-by: Yacov Manevich <yacovm@il.ibm.com>

Co-authored-by: yacovm <yacovm@li-3faaf6cc-2cd1-11b2-a85c-fd3f1da7bbdb.ibm.com>

## Patch
### orderer/common/cluster/comm_test.go
```diff
@@ -197,6 +197,11 @@ func (cn *clusterNode) stop() {
 }
 
 func (cn *clusterNode) renewCertificates() {
+	// Stop the gRPC service
+	cn.srv.Stop()
+	// and restart it afterwards
+	defer cn.resurrect()
+
 	clientKeyPair, err := ca.NewClientCertKeyPair()
 	if err != nil {
 		panic(fmt.Errorf("failed creating client certificate %v", err))
@@ -852,10 +857,9 @@ func TestReconnect(t *testing.T) {
 
 func TestRenewCertificates(t *testing.T) {
 	// Scenario: node 1 and node 2 are connected,
-	// and the certificates are renewed for both nodes
-	// at the same time.
-	// They are expected to connect to one another
-	// after the reconfiguration.
+	// Node 2's certificate is renewed, and
+	// node 1 is reconfigured with the new
+	// configuration without being restarted.
 
 	node1 := newTestNode(t)
 	defer node1.stop()
@@ -872,34 +876,25 @@ func TestRenewCertificates(t *testing.T) {
 
 	assertBiDiCommunication(t, node1, node2, testReq)
 
-	// Now, renew certificates both both nodes
-	node1.renewCertificates()
+	// Close outgoing connections from node2 to node1
+	node2.c.Configure(testChannel, nil)
+	// Renew node 2's keys
 	node2.renewCertificates()
 
-	// Reconfigure them
-	config = []cluster.RemoteNode{node1.nodeInfo, node2.nodeInfo}
-	node1.c.Configure(testChannel, config)
-	node2.c.Configure(testChannel, config)
-
 	// W.L.O.G, try to send a message from node1 to node2
 	// It should fail, because node2's server certificate has now changed,
 	// so it closed the connection to the remote node
 	info2 := node2.nodeInfo
 	remote, err := node1.c.Remote(testChannel, info2.ID)
 	require.NoError(t, err)
 	require.NotNil(t, remote)
+	_, err = remote.NewStream(time.Hour)
+	require.Contains(t, err.Error(), info2.Endpoint)
 
-	gt := gomega.NewGomegaWithT(t)
-	gt.Eventually(func() string {
-		_, err = remote.NewStream(time.Hour)
-		return err.Error()
-	}, timeout).Should(gomega.ContainSubstring(info2.Endpoint))
-
-	// Restart the gRPC service on both nodes, to load the new TLS certificates
-	node1.srv.Stop()
-	node1.resurrect()
-	node2.srv.Stop()
-	node2.resurrect()
+	// Reconfigure both nodes with the updates keys
+	config = []cluster.RemoteNode{node1.nodeInfo, node2.nodeInfo}
+	node1.c.Configure(testChannel, config)
+	node2.c.Configure(testChannel, config)
 
 	// Finally, check that the nodes can communicate once again
 	assertBiDiCommunication(t, node1, node2, testReq)
@@ -1372,7 +1367,6 @@ func assertBiDiCommunicationForChannel(t *testing.T, node1, node2 *clusterNode,
 		{label: "2->1", sender: node2, target: node1.nodeInfo.ID, receiver: node1},
 	}
 	for _, estab := range establish {
-		t.Log(estab.label)
 		stub, err := estab.sender.c.Remote(channel, estab.target)
 		require.NoError(t, err)
 
@@ -1383,6 +1377,7 @@ func assertBiDiCommunicationForChannel(t *testing.T, node1, node2 *clusterNode,
 		estab.receiver.handler.On("OnSubmit", channel, estab.sender.nodeInfo.ID, mock.Anything).Return(nil).Once().Run(func(args mock.Arguments) {
 			req := args.Get(2).(*orderer.SubmitRequest)
 			require.True(t, proto.Equal(req, msgToSend))
+			t.Log(estab.label)
 			wg.Done()
 		})
 
```
