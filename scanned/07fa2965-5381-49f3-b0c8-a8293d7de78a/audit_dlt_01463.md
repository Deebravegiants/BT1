# [?] graph/db/models: fix race condition in Node.PubKey

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2025-12-04
Source: https://github.com/lightningnetwork/lnd/commit/9906e61774816ab29b1755a3ab9e0f1036cab439
Type: security-commit

## Details
graph/db/models: fix race condition in Node.PubKey

The PubKey method had a race condition where concurrent calls could
all pass the nil check and race to write to the cached pubKey field.
This is a classic check-then-act race.

Remove the caching entirely to fix the race. The overhead of parsing
a public key is minimal and doesn't justify the added complexity and
race risk of caching.

## Patch
### graph/db/models/node.go
```diff
@@ -22,7 +22,6 @@ type Node struct {
 
 	// PubKeyBytes is the raw bytes of the public key of the target node.
 	PubKeyBytes [33]byte
-	pubKey      *btcec.PublicKey
 
 	// LastUpdate is the last time the vertex information for this node has
 	// been updated.
@@ -129,21 +128,8 @@ func (n *Node) HaveAnnouncement() bool {
 
 // PubKey is the node's long-term identity public key. This key will be used to
 // authenticated any advertisements/updates sent by the node.
-//
-// NOTE: By having this method to access an attribute, we ensure we only need
-// to fully deserialize the pubkey if absolutely necessary.
 func (n *Node) PubKey() (*btcec.PublicKey, error) {
-	if n.pubKey != nil {
-		return n.pubKey, nil
-	}
-
-	key, err := btcec.ParsePubKey(n.PubKeyBytes[:])
-	if err != nil {
-		return nil, err
-	}
-	n.pubKey = key
-
-	return key, nil
+	return btcec.ParsePubKey(n.PubKeyBytes[:])
 }
 
 // NodeAnnouncement retrieves the latest node announcement of the node.
```
