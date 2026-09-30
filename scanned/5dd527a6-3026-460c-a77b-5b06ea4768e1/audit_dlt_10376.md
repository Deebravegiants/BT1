# [?] fix crash in test (#3)

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2018-10-09
Source: https://github.com/0xsoniclabs/sonic/commit/ef4db02eaba1674bc53bffbc1cc8bfac8bd5ecde
Type: security-commit

## Details
fix crash in test (#3)

## Patch
### tester/tester.go
```diff
@@ -26,7 +26,7 @@ func PingNodesN(participants []*peers.Peer, p peers.PubKeyPeers, n uint64, servi
 	for i := uint64(0); i < n; i++ {
 		wg.Add(1)
 		participant := participants[rand.Intn(len(participants))]
-		node := p[participant.NetAddr]
+		node := p[participant.PubKeyHex]
 
 		ipAddr, err := transact(*participant, node.ID, txId, serviceAddress)
 		if err != nil {
```
