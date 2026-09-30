# [?] Implemented @jbenet's suggestion to avoid panics if peerID is of length 0.

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2015-03-03
Source: https://github.com/libp2p/go-libp2p/commit/236dfd1e1837552a9dd85915f0b1348e6d1444c2
Type: security-commit

## Details
Implemented @jbenet's suggestion to avoid panics if peerID is of length 0.

## Patch
### peer/peer.go
```diff
@@ -5,6 +5,7 @@ import (
 	"encoding/hex"
 	"encoding/json"
 	"fmt"
+	"strings"
 
 	b58 "github.com/jbenet/go-ipfs/Godeps/_workspace/src/github.com/jbenet/go-base58"
 	ma "github.com/jbenet/go-ipfs/Godeps/_workspace/src/github.com/jbenet/go-multiaddr"
@@ -38,12 +39,18 @@ func (id ID) Loggable() map[string]interface{} {
 // codebase is known to be correct.
 func (id ID) String() string {
 	pid := id.Pretty()
+
+	//All sha256 nodes start with Qm
+	//We can skip the Qm to make the peer.ID more useful
+	if strings.HasPrefix(pid, "Qm") {
+		pid = pid[2:]
+	}
+
 	maxRunes := 6
-	skip := 2 //Added to skip past Qm which is identical for all SHA256 nodes	
-	if len(pid) < maxRunes + skip {
-		maxRunes = len(pid) - skip
+	if len(pid) < maxRunes {
+		maxRunes = len(pid)
 	}
-	return fmt.Sprintf("<peer.ID %s>", pid[skip:maxRunes + skip])
+	return fmt.Sprintf("<peer.ID %s>", pid[:maxRunes])
 }
 
 // MatchesPrivateKey tests whether this ID was derived from sk
```
