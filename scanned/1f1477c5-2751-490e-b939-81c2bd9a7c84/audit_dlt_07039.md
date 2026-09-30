# [?] p2p/discover: fix crash when revalidated node is removed (#29864)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2024-05-28
Source: https://github.com/ethereum/go-ethereum/commit/af0a3274be0f948f4816142394559f2d02475980
Type: security-commit

## Details
p2p/discover: fix crash when revalidated node is removed (#29864)

In #29572, I assumed the revalidation list that the node is contained in could only ever
be changed by the outcome of a revalidation request. But turns out that's not true: if the
node gets removed due to FINDNODE failure, it will also be removed from the list it is in.
This causes a crash.

The invariant is: while node is in table, it is always in exactly one of the two lists. So
it seems best to store a pointer to the current list within the node itself.

## Patch
### p2p/discover/node.go
```diff
@@ -41,6 +41,7 @@ type BucketNode struct {
 // The fields of Node may not be modified.
 type node struct {
 	*enode.Node
+	revalList       *revalidationList
 	addedToTable    time.Time // first time node was added to bucket or replacement list
 	addedToBucket   time.Time // time it was added in the actual bucket
 	livenessChecks  uint      // how often liveness was checked
```

### p2p/discover/table_reval.go
```diff
@@ -39,7 +39,6 @@ type tableRevalidation struct {
 type revalidationResponse struct {
 	n          *node
 	newRecord  *enode.Node
-	list       *revalidationList
 	didRespond bool
 }
 
@@ -60,34 +59,35 @@ func (tr *tableRevalidation) nodeAdded(tab *Table, n *node) {
 
 // nodeRemoved is called when a node was removed from the table.
 func (tr *tableRevalidation) nodeRemoved(n *node) {
-	if !tr.fast.remove(n) {
-		tr.slow.remove(n)
+	if n.revalList == nil {
+		panic(fmt.Errorf("removed node %v has nil revalList", n.ID()))
 	}
+	n.revalList.remove(n)
 }
 
 // run performs node revalidation.
 // It returns the next time it should be invoked, which is used in the Table main loop
 // to schedule a timer. However, run can be called at any time.
 func (tr *tableRevalidation) run(tab *Table, now mclock.AbsTime) (nextTime mclock.AbsTime) {
 	if n := tr.fast.get(now, &tab.rand, tr.activeReq); n != nil {
-		tr.startRequest(tab, &tr.fast, n)
+		tr.startRequest(tab, n)
 		tr.fast.schedule(now, &tab.rand)
 	}
 	if n := tr.slow.get(now, &tab.rand, tr.activeReq); n != nil {
-		tr.startRequest(tab, &tr.slow, n)
+		tr.startRequest(tab, n)
 		tr.slow.schedule(now, &tab.rand)
 	}
 
 	return min(tr.fast.nextTime, tr.slow.nextTime)
 }
 
 // startRequest spawns a revalidation request for node n.
-func (tr *tableRevalidation) startRequest(tab *Table, list *revalidationList, n *node) {
+func (tr *tableRevalidation) startRequest(tab *Table, n *node) {
 	if _, ok := tr.activeReq[n.ID()]; ok {
-		panic(fmt.Errorf("duplicate startRequest (list %q, node %v)", list.name, n.ID()))
+		panic(fmt.Errorf("duplicate startRequest (node %v)", n.ID()))
 	}
 	tr.activeReq[n.ID()] = struct{}{}
-	resp := revalidationResponse{n: n, list: list}
+	resp := revalidationResponse{n: n}
 
 	// Fetch the node while holding lock.
 	tab.mutex.Lock()
@@ -120,11 +120,28 @@ func (tab *Table) doRevalidate(resp revalidationResponse, node *enode.Node) {
 
 // handleResponse processes the result of a revalidation request.
 func (tr *tableRevalidation) handleResponse(tab *Table, resp revalidationResponse) {
-	now := tab.cfg.Clock.Now()
-	n := resp.n
-	b := tab.bucket(n.ID())
+	var (
+		now = tab.cfg.Clock.Now()
+		n   = resp.n
+		b   = tab.bucket(n.ID())
+	)
 	delete(tr.activeReq, n.ID())
 
+	// If the node was removed from the table while getting checked, we need to stop
+	// processing here to avoid re-adding it.
+	if n.revalList == nil {
+		return
+	}
+
+	// Store potential seeds in database.
+	// This is done via defer to avoid holding Table lock while writing to DB.
+	defer func() {
+		if n.isValidatedLive && n.livenessChecks > 5 {
+			tab.db.UpdateNode(resp.n.Node)
+		}
+	}()
+
+	// Remaining logic needs access to Table internals.
 	tab.mutex.Lock()
 	defer tab.mutex.Unlock()
 
@@ -134,7 +151,7 @@ func (tr *tableRevalidation) handleResponse(tab *Table, resp revalidationRespons
 		if n.livenessChecks <= 0 {
 			tab.deleteInBucket(b, n.ID())
 		} else {
-			tr.moveToList(&tr.fast, resp.list, n, now, &tab.rand)
+			tr.moveToList(&tr.fast, n, now, &tab.rand)
 		}
 		return
 	}
@@ -151,27 +168,23 @@ func (tr *tableRevalidation) handleResponse(tab *Table, resp revalidationRespons
 			n.isValidatedLive = false
 		}
 	}
-	tab.log.Debug("Revalidated node", "b", b.index, "id", n.ID(), "checks", n.livenessChecks, "q", resp.list.name)
+	tab.log.Debug("Revalidated node", "b", b.index, "id", n.ID(), "checks", n.livenessChecks, "q", n.revalList)
 
 	// Move node over to slow queue after first validation.
 	if !endpointChanged {
-		tr.moveToList(&tr.slow, resp.list, n, now, &tab.rand)
+		tr.moveToList(&tr.slow, n, now, &tab.rand)
 	} else {
-		tr.moveToList(&tr.fast, resp.list, n, now, &tab.rand)
-	}
-
-	// Store potential seeds in database.
-	if n.isValidatedLive && n.livenessChecks > 5 {
-		tab.db.UpdateNode(resp.n.Node)
+		tr.moveToList(&tr.fast, n, now, &tab.rand)
 	}
 }
 
-func (tr *tableRevalidation) moveToList(dest, source *revalidationList, n *node, now mclock.AbsTime, rand randomSource) {
-	if source == dest {
+// moveToList ensures n is in the 'dest' list.
+func (tr *tableRevalidation) moveToList(dest *revalidationList, n *node, now mclock.AbsTime, rand randomSource) {
+	if n.revalList == dest {
 		return
 	}
-	if !source.remove(n) {
-		panic(fmt.Errorf("moveToList(%q -> %q): node %v not in source list", source.name, dest.name, n.ID()))
+	if n.revalList != nil {
+		n.revalList.remove(n)
 	}
 	dest.push(n, now, rand)
 }
@@ -208,16 +221,23 @@ func (list *revalidationList) push(n *node, now mclock.AbsTime, rand randomSourc
 	if list.nextTime == never {
 		list.schedule(now, rand)
 	}
+	n.revalList = list
 }
 
-func (list *revalidationList) remove(n *node) bool {
+func (list *revalidationList) remove(n *node) {
 	i := slices.Index(list.nodes, n)
 	if i == -1 {
-		return false
+		panic(fmt.Errorf("node %v not found in list", n.ID()))
 	}
 	list.nodes = slices.Delete(list.nodes, i, i+1)
 	if len(list.nodes) == 0 {
 		list.nextTime = never
 	}
-	return true
+	n.revalList = nil
+}
+
+func (list *revalidationList) contains(id enode.ID) bool {
+	return slices.ContainsFunc(list.nodes, func(n *node) bool {
+		return n.ID() == id
+	})
 }
```

### p2p/discover/table_reval_test.go
```diff
@@ -0,0 +1,70 @@
+// Copyright 2024 The go-ethereum Authors
+// This file is part of the go-ethereum library.
+//
+// The go-ethereum library is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// The go-ethereum library is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with the go-ethereum library. If not, see <http://www.gnu.org/licenses/>.
+
+package discover
+
+import (
+	"net"
+	"testing"
+	"time"
+
+	"github.com/ethereum/go-ethereum/common/mclock"
+)
+
+// This test checks that revalidation can handle a node disappearing while
+// a request is active.
+func TestRevalidationNodeRemoved(t *testing.T) {
+	var (
+		clock     mclock.Simulated
+		transport = newPingRecorder()
+		tab, db   = newInactiveTestTable(transport, Config{Clock: &clock})
+		tr        = &tab.revalidation
+	)
+	defer db.Close()
+
+	// Fill a bucket.
+	node := nodeAtDistance(tab.self().ID(), 255, net.IP{77, 88, 99, 1})
+	tab.handleAddNode(addNodeOp{node: node})
+
+	// Start a revalidation request. Schedule once to get the next start time,
+	// then advance the clock to that point and schedule again to start.
+	next := tr.run(tab, clock.Now())
+	clock.Run(time.Duration(next + 1))
+	tr.run(tab, clock.Now())
+	if len(tr.activeReq) != 1 {
+		t.Fatal("revalidation request did not start:", tr.activeReq)
+	}
+
+	// Delete the node.
+	tab.deleteInBucket(tab.bucket(node.ID()), node.ID())
+
+	// Now finish the revalidation request.
+	var resp revalidationResponse
+	select {
+	case resp = <-tab.revalResponseCh:
+	case <-time.After(1 * time.Second):
+		t.Fatal("timed out waiting for revalidation")
+	}
+	tr.handleResponse(tab, resp)
+
+	// Ensure the node was not re-added to the table.
+	if tab.getNode(node.ID()) != nil {
+		t.Fatal("node was re-added to Table")
+	}
+	if tr.fast.contains(node.ID()) || tr.slow.contains(node.ID()) {
+		t.Fatal("removed node contained in revalidation list")
+	}
+}
```

### p2p/discover/table_util_test.go
```diff
@@ -43,9 +43,15 @@ func init() {
 }
 
 func newTestTable(t transport, cfg Config) (*Table, *enode.DB) {
+	tab, db := newInactiveTestTable(t, cfg)
+	go tab.loop()
+	return tab, db
+}
+
+// newInactiveTestTable creates a Table without running the main loop.
+func newInactiveTestTable(t transport, cfg Config) (*Table, *enode.DB) {
 	db, _ := enode.OpenDB("")
 	tab, _ := newTable(t, db, cfg)
-	go tab.loop()
 	return tab, db
 }
 
```
