# [?] fix: harness tests random panic (#10933)

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2025-08-22
Source: https://github.com/ipfs/kubo/commit/ae068a806181dc09d4d679ba8d3c6e5f3547afac
Type: security-commit

## Details
fix: harness tests random panic (#10933)

* fix: harness tests random panic

Connecting nodes in parallel can cause TLS handshake failures. For each node, connect to the other nodes serially. It is not necessary to connect in parallel as it does not save any significant time.

Closes #10932

## Patch
### test/cli/harness/nodes.go
```diff
@@ -5,7 +5,6 @@ import (
 
 	. "github.com/ipfs/kubo/test/cli/testutils"
 	"github.com/multiformats/go-multiaddr"
-	"golang.org/x/sync/errgroup"
 )
 
 // Nodes is a collection of Kubo nodes along with operations on groups of nodes.
@@ -17,37 +16,28 @@ func (n Nodes) Init(args ...string) Nodes {
 }
 
 func (n Nodes) ForEachPar(f func(*Node)) {
-	group := &errgroup.Group{}
+	var wg sync.WaitGroup
 	for _, node := range n {
+		wg.Add(1)
 		node := node
-		group.Go(func() error {
+		go func() {
+			defer wg.Done()
 			f(node)
-			return nil
-		})
-	}
-	err := group.Wait()
-	if err != nil {
-		panic(err)
+		}()
 	}
+	wg.Wait()
 }
 
 func (n Nodes) Connect() Nodes {
-	wg := sync.WaitGroup{}
 	for i, node := range n {
 		for j, otherNode := range n {
 			if i == j {
 				continue
 			}
-			node := node
-			otherNode := otherNode
-			wg.Add(1)
-			go func() {
-				defer wg.Done()
-				node.Connect(otherNode)
-			}()
+			// Do not connect in parallel, because that can cause TLS handshake problems on some platforms.
+			node.Connect(otherNode)
 		}
 	}
-	wg.Wait()
 	for _, node := range n {
 		firstPeer := node.Peers()[0]
 		if _, err := firstPeer.ValueForProtocol(multiaddr.P_P2P); err != nil {
```
