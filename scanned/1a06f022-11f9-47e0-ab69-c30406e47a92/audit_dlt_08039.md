# [?] p2p/discover: fix crash in Resolve (#19579)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-05-15
Source: https://github.com/celo-org/celo-blockchain/commit/b548b5aeb00dd51f4f2d982f60d9dec5af8615e8
Type: security-commit

## Details
p2p/discover: fix crash in Resolve (#19579)

## Patch
### p2p/discover/v4_udp.go
```diff
@@ -426,11 +426,11 @@ func (t *UDPv4) Resolve(n *enode.Node) *enode.Node {
 		}
 	}
 	// Otherwise perform a network lookup.
-	var key *enode.Secp256k1
-	if n.Load(key) != nil {
+	var key enode.Secp256k1
+	if n.Load(&key) != nil {
 		return n // no secp256k1 key
 	}
-	result := t.LookupPubkey((*ecdsa.PublicKey)(key))
+	result := t.LookupPubkey((*ecdsa.PublicKey)(&key))
 	for _, rn := range result {
 		if rn.ID() == n.ID() {
 			if rn, err := t.requestENR(rn); err == nil {
```
