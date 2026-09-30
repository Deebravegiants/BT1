# [?] swarm/network: fix data race in TestNetworkID test (#18460)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-01-16
Source: https://github.com/celo-org/celo-blockchain/commit/e63995b3f36837b97330a7ccaf56277099904d26
Type: security-commit

## Details
swarm/network: fix data race in TestNetworkID test (#18460)

(cherry picked from commit 96c7c18b184ae894f1c6bd5fbfc45fbcfa9ace77)

## Patch
### swarm/network/networkid_test.go
```diff
@@ -76,13 +76,12 @@ func TestNetworkID(t *testing.T) {
 	if err != nil {
 		t.Fatalf("Error setting up network: %v", err)
 	}
-	defer func() {
-		//shutdown the snapshot network
-		log.Trace("Shutting down network")
-		net.Shutdown()
-	}()
 	//let's sleep to ensure all nodes are connected
 	time.Sleep(1 * time.Second)
+	// shutdown the the network to avoid race conditions
+	// on accessing kademlias global map while network nodes
+	// are accepting messages
+	net.Shutdown()
 	//for each group sharing the same network ID...
 	for _, netIDGroup := range nodeMap {
 		log.Trace("netIDGroup size", "size", len(netIDGroup))
```
