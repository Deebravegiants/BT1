# [?] fix deadlock for fast storage

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2023-03-06
Source: https://github.com/sei-protocol/sei-chain/commit/91605bae72364e8bbb3818f010a0c8689f9b084d
Type: security-commit

## Details
fix deadlock for fast storage

## Patch
### sei-iavl/iterator.go
```diff
@@ -17,11 +17,12 @@ type traversal struct {
 	inclusive    bool          // end key inclusiveness
 	post         bool          // postorder traversal
 	delayedNodes *delayedNodes // delayed nodes to be traversed
+	unlocked     bool          // whether traversal should not lock tree's mutex
 }
 
 var errIteratorNilTreeGiven = errors.New("iterator must be created with an immutable tree but the tree was nil")
 
-func (node *Node) newTraversal(tree *ImmutableTree, start, end []byte, ascending bool, inclusive bool, post bool) *traversal {
+func (node *Node) newTraversal(tree *ImmutableTree, start, end []byte, ascending bool, inclusive bool, post bool, unlocked bool) *traversal {
 	return &traversal{
 		tree:         tree,
 		start:        start,
@@ -30,6 +31,7 @@ func (node *Node) newTraversal(tree *ImmutableTree, start, end []byte, ascending
 		inclusive:    inclusive,
 		post:         post,
 		delayedNodes: &delayedNodes{{node, true}}, // set initial traverse to the node
+		unlocked:     unlocked,
 	}
 }
 
@@ -100,8 +102,10 @@ func (t *traversal) next() (*Node, error) {
 }
 
 func (t *traversal) doNext() (*Node, error, bool) {
-	// t.tree.mtx.Lock()
-	// defer t.tree.mtx.Unlock()
+	if !t.unlocked {
+		t.tree.mtx.Lock()
+		defer t.tree.mtx.Unlock()
+	}
 
 	// End of traversal.
 	if t.delayedNodes.length() == 0 {
@@ -206,7 +210,24 @@ func NewIterator(start, end []byte, ascending bool, tree *ImmutableTree) dbm.Ite
 		iter.err = errIteratorNilTreeGiven
 	} else {
 		iter.valid = true
-		iter.t = tree.root.newTraversal(tree, start, end, ascending, false, false)
+		iter.t = tree.root.newTraversal(tree, start, end, ascending, false, false, false)
+		// Move iterator before the first element
+		iter.Next()
+	}
+	return iter
+}
+
+func NewIteratorUnlocked(start, end []byte, ascending bool, tree *ImmutableTree) dbm.Iterator {
+	iter := &Iterator{
+		start: start,
+		end:   end,
+	}
+
+	if tree == nil {
+		iter.err = errIteratorNilTreeGiven
+	} else {
+		iter.valid = true
+		iter.t = tree.root.newTraversal(tree, start, end, ascending, false, false, true)
 		// Move iterator before the first element
 		iter.Next()
 	}
```

### sei-iavl/mutable_tree.go
```diff
@@ -712,7 +712,7 @@ func (tree *MutableTree) enableFastStorageAndCommitIfNotEnabled() (bool, error)
 func (tree *MutableTree) enableFastStorageAndCommit() error {
 	var err error
 
-	itr := NewIterator(nil, nil, true, tree.ImmutableTree)
+	itr := NewIteratorUnlocked(nil, nil, true, tree.ImmutableTree)
 	defer itr.Close()
 	var upgradedFastNodes uint64
 	for ; itr.Valid(); itr.Next() {
@@ -1120,13 +1120,14 @@ func (tree *MutableTree) DeleteVersionsRange(fromVersion, toVersion int64) error
 // longer be accessed.
 func (tree *MutableTree) DeleteVersion(version int64) error {
 	logger.Debug("DELETE VERSION: %d\n", version)
-	tree.mtx.Lock()
-	defer tree.mtx.Unlock()
 
 	if err := tree.deleteVersion(version); err != nil {
 		return err
 	}
 
+	tree.mtx.Lock()
+	defer tree.mtx.Unlock()
+
 	if err := tree.ndb.Commit(); err != nil {
 		return err
 	}
```

### sei-iavl/node.go
```diff
@@ -147,21 +147,6 @@ func (node *Node) clone(version int64) (*Node, error) {
 	}, nil
 }
 
-func (node *Node) cloneAny() *Node {
-	return &Node{
-		key:       node.key,
-		height:    node.height,
-		version:   node.version,
-		size:      node.size,
-		hash:      nil,
-		leftHash:  node.leftHash,
-		leftNode:  node.leftNode,
-		rightHash: node.rightHash,
-		rightNode: node.rightNode,
-		persisted: false,
-	}
-}
-
 func (node *Node) isLeaf() bool {
 	return node.height == 0
 }
@@ -552,7 +537,7 @@ func (node *Node) traversePost(t *ImmutableTree, ascending bool, cb func(*Node)
 
 func (node *Node) traverseInRange(tree *ImmutableTree, start, end []byte, ascending bool, inclusive bool, post bool, cb func(*Node) bool) bool {
 	stop := false
-	t := node.newTraversal(tree, start, end, ascending, inclusive, post)
+	t := node.newTraversal(tree, start, end, ascending, inclusive, post, false)
 	// TODO: figure out how to handle these errors
 	for node2, err := t.next(); node2 != nil && err == nil; node2, err = t.next() {
 		stop = cb(node2)
```

### sei-iavl/nodedb.go
```diff
@@ -118,7 +118,7 @@ func (ndb *nodeDB) GetNode(hash []byte) (*Node, error) {
 	// Check the cache.
 	if cachedNode := ndb.nodeCache.Get(hash); cachedNode != nil {
 		ndb.opts.Stat.IncCacheHitCnt()
-		return cachedNode.(*Node).cloneAny(), nil
+		return cachedNode.(*Node), nil
 	}
 
 	ndb.opts.Stat.IncCacheMissCnt()
@@ -139,7 +139,7 @@ func (ndb *nodeDB) GetNode(hash []byte) (*Node, error) {
 
 	node.hash = hash
 	node.persisted = true
-	ndb.nodeCache.Add(node.cloneAny())
+	ndb.nodeCache.Add(node)
 
 	return node, nil
 }
@@ -206,7 +206,7 @@ func (ndb *nodeDB) SaveNode(node *Node) error {
 	}
 	logger.Debug("BATCH SAVE %X %p\n", node.hash, node)
 	node.persisted = true
-	ndb.nodeCache.Add(node.cloneAny())
+	ndb.nodeCache.Add(node)
 	return nil
 }
 
```
