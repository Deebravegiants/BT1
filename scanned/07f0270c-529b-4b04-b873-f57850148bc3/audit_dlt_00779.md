# [?] Fix rpc hash race condition (#3693)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2026-07-02
Source: https://github.com/sei-protocol/sei-chain/commit/ae66b4fe0b5812c1287cb67e79786533abca5b56
Type: security-commit

## Details
Fix rpc hash race condition (#3693)

## Fix
Serialize the hash-mutating operations on each memIAVL tree with the
tree's
**write** lock, and add no-lock internal helpers so the public entry
points
don't re-acquire the lock recursively.
`sei-db/state_db/sc/memiavl/tree.go`
- `RootHash()` now takes `t.mtx.Lock()` (it mutates `MemNode.hash`),
delegating to a new `rootHashNoLock()`.
- `GetProof()` now takes `t.mtx.Lock()` for the whole proof build,
delegating to `getProofNoLock()`.
- Added no-lock read helpers used by the proof builders:
`getWithIndexNoLock()`, `getByIndexNoLock()`, `hasNoLock()`.
`sei-db/state_db/sc/memiavl/proof.go`
- `GetMembershipProof()` / `GetNonMembershipProof()` now take the write
lock and delegate to `getMembershipProofNoLock()` /
`getNonMembershipProofNoLock()`.
- `createExistenceProof()` documented as "caller must hold the write
lock".
The read-only fast paths (`Get`, `GetWithIndex`, `GetByIndex`, `Has`,
`Iterator`)
are unchanged and still use `RLock`. Locking is **per-tree
(per-store)**.
### Lock-ordering safety
- Commit path acquires `db.mtx` then per-tree `t.mtx`; the query path
acquires
  only `t.mtx`. No inversion, no new deadlock.
- No in-package caller invokes the now-locking methods while already
holding
  `t.mtx` (verified); internal callers use the `*NoLock` helpers.
## Performance impact
- **Validators (no queries):** the write lock is uncontended, so
`Lock()` costs
the same as the previous `RLock()` (a single atomic op). `RootHash` runs
~once/twice per store per block → single-digit microseconds per block.
No
  measurable impact on block/consensus/tx-execution time.
- **Tx execution:** unaffected — reads go through cache stores (`RLock`,
  unchanged); `GetProof` is not on the execution path.
- **RPC nodes under heavy `prove=true`:** a commit's `RootHash` and a
proof build
now serialize **per store**. This is bounded (proof build is O(tree
height))
and per-store (committing store A never blocks proofs on store B). It is
the
necessary cost of correctness — the previous "cheaper" path was the bug.
## Testing
Added `sei-db/state_db/sc/memiavl/tree_race_test.go`:
- `TestTreeProofRaceWithCommit` — commit (`Set` + `RootHash`) concurrent
with
  membership/non-membership `GetProof` and `RootHash`.
- `TestTreeConcurrentRootHash` — concurrent `RootHash` over a tree with
unfilled
  hash caches; asserts all callers agree.
Verification:
- The tests were confirmed to **reproduce** the bug: reverting the two
locks back
  to `RLock` makes `go test -race` report `DATA RACE` on `MemNode.hash`.
- With the fix, `go test -race ./sei-db/state_db/sc/memiavl/...` passes
clean
  (0 data races), as do the `commitment` and `rootmulti` suites.
## Risk & rollout
- Read-path behavior and hash outputs are unchanged; this is a
locking-only fix.
- Safe to roll out without coordination (not AppHash-format changing).
It
  *prevents* divergence rather than changing committed state.

### sei-db/state_db/sc/memiavl/proof.go
```diff
@@ -27,6 +27,15 @@ GetMembershipProof will produce a CommitmentProof that the given key (and querie
 If the key doesn't exist in the tree, this will return an error.
 */
 func (t *Tree) GetMembershipProof(key []byte) (*ics23.CommitmentProof, error) {
+	t.mtx.Lock()
+	defer t.mtx.Unlock()
+	return t.getMembershipProofNoLock(key)
+}
+
+// getMembershipProofNoLock is GetMembershipProof without acquiring t.mtx; the
+// caller must already hold the write lock (createExistenceProof mutates
+// MemNode.hash via Node.Hash()).
+func (t *Tree) getMembershipProofNoLock(key []byte) (*ics23.CommitmentProof, error) {
 	exist, err := t.createExistenceProof(key)
 	if err != nil {
 		return nil, err
@@ -40,6 +49,13 @@ func (t *Tree) GetMembershipProof(key []byte) (*ics23.CommitmentProof, error) {
 }
 
 // VerifyMembership returns true iff proof is an ExistenceProof for the given key.
+//
+// NOTE: this reads the value (Get, RLock) and the root (RootHash, write lock)
+// under two separate lock acquisitions, so a commit landing between them can
+// yield an inconsistent (val, root) pair. That is acceptable here because this
+// is a test/verification-only helper and is not used on the live commit or
+// query paths; a caller needing an atomic (value, root) snapshot must serialize
+// against commits itself.
 func (t *Tree) VerifyMembership(proof *ics23.CommitmentProof, key []byte) bool {
 	val := t.Get(key)
 	root := t.RootHash()
@@ -51,9 +67,18 @@ GetNonMembershipProof will produce a CommitmentProof that the given key doesn't
 If the key exists in the tree, this will return an error.
 */
 func (t *Tree) GetNonMembershipProof(key []byte) (*ics23.CommitmentProof, error) {
+	t.mtx.Lock()
+	defer t.mtx.Unlock()
+	return t.getNonMembershipProofNoLock(key)
+}
+
+// getNonMembershipProofNoLock is GetNonMembershipProof without acquiring
+// t.mtx; the caller must already hold the write lock. It uses the *NoLock
+// read helpers so it does not recursively re-acquire t.mtx.
+func (t *Tree) getNonMembershipProofNoLock(key []byte) (*ics23.CommitmentProof, error) {
 	// idx is one node right of what we want....
 	var err error
-	idx, val := t.GetWithIndex(key)
+	idx, val := t.getWithIndexNoLock(key)
 	if val != nil {
 		return nil, fmt.Errorf("cannot create NonExistanceProof when Key in State")
 	}
@@ -63,15 +88,15 @@ func (t *Tree) GetNonMembershipProof(key []byte) (*ics23.CommitmentProof, error)
 	}
 
 	if idx >= 1 {
-		leftkey, _ := t.GetByIndex(idx - 1)
+		leftkey, _ := t.getByIndexNoLock(idx - 1)
 		nonexist.Left, err = t.createExistenceProof(leftkey)
 		if err != nil {
 			return nil, err
 		}
 	}
 
 	// this will be nil if nothing right of the queried key
-	rightkey, _ := t.GetByIndex(idx)
+	rightkey, _ := t.getByIndexNoLock(idx)
 	if rightkey != nil {
 		nonexist.Right, err = t.createExistenceProof(rightkey)
 		if err != nil {
@@ -88,13 +113,22 @@ func (t *Tree) GetNonMembershipProof(key []byte) (*ics23.CommitmentProof, error)
 }
 
 // VerifyNonMembership returns true iff proof is a NonExistenceProof for the given key.
+//
+// NOTE: like VerifyMembership, this is a test/verification-only helper. The
+// supplied proof and the root read here (RootHash, write lock) are not captured
+// atomically relative to concurrent commits, so it must not be relied on for
+// consistency on the live commit or query paths.
 func (t *Tree) VerifyNonMembership(proof *ics23.CommitmentProof, key []byte) bool {
 	root := t.RootHash()
 	return ics23.VerifyNonMembership(ics23.IavlSpec, root, proof, key)
 }
 
 // createExistenceProof will get the proof from the tree and convert the proof into a valid
 // existence proof, if that's what it is.
+//
+// It reads t.root and sibling node hashes (via Node.Hash(), which mutates
+// MemNode.hash in place), so the caller must already hold t.mtx's write lock.
+// All in-tree callers reach it through the *NoLock proof builders.
 func (t *Tree) createExistenceProof(key []byte) (*ics23.ExistenceProof, error) {
 	path, node, err := pathToLeaf(t.root, key)
 	return &ics23.ExistenceProof{
```

### sei-db/state_db/sc/memiavl/tree.go
```diff
@@ -30,7 +30,18 @@ type Tree struct {
 	// when true, the get and iterator methods could return a slice pointing to mmaped blob files.
 	zeroCopy bool
 
-	// sync.RWMutex is used to protect the tree for thread safety during snapshot reload
+	// mtx guards concurrent access to this tree's mutable state (root, version,
+	// cowVersion, snapshot) AND the lazily-populated MemNode.hash caches reachable
+	// from root. Operations that fill those caches in place — RootHash and the
+	// proof builders (GetProof/GetMembership/GetNonMembership) — take the write
+	// lock; pure reads (Get/Has/Iterator) take the read lock. This serialization
+	// only protects a single tree instance: a tree produced by Copy() gets its
+	// own mtx and shares the underlying nodes copy-on-write. Cross-copy hash
+	// consistency therefore relies on (a) the shared nodes already being fully
+	// hashed before the copy is used for hashing/proofs (Copy is taken between
+	// commits, and the commit path hashes via SaveVersion(true)/RootHash), and
+	// (b) cowVersion cloning any shared MemNode before it is structurally mutated,
+	// so a live-tree write never mutates a node another copy is still reading.
 	mtx *sync.RWMutex
 
 	pendingChanges chan proto.ChangeSet
@@ -192,9 +203,23 @@ func (t *Tree) Version() int64 {
 
 // RootHash updates the hashes and return the current root hash,
 // it clones the persisted node's bytes, so the returned bytes is safe to retain.
+//
+// It takes the write lock (not RLock) because Hash() lazily populates
+// MemNode.hash in place on the live nodes. Two goroutines mutating that
+// shared cache under a read lock — e.g. a commit's RootHash racing a
+// latest-height proof query's GetProof — is a data race that can serialize
+// a stale internal hash into the store root and diverge the AppHash
+// (Immunefi 83246 / STO-601). Callers that already hold t.mtx must use
+// rootHashNoLock instead.
 func (t *Tree) RootHash() []byte {
-	t.mtx.RLock()
-	defer t.mtx.RUnlock()
+	t.mtx.Lock()
+	defer t.mtx.Unlock()
+	return t.rootHashNoLock()
+}
+
+// rootHashNoLock is RootHash without acquiring t.mtx; the caller must already
+// hold the write lock.
+func (t *Tree) rootHashNoLock() []byte {
 	if t.root == nil {
 		return emptyHash
 	}
@@ -204,6 +229,13 @@ func (t *Tree) RootHash() []byte {
 func (t *Tree) GetWithIndex(key []byte) (int64, []byte) {
 	t.mtx.RLock()
 	defer t.mtx.RUnlock()
+	return t.getWithIndexNoLock(key)
+}
+
+// getWithIndexNoLock is GetWithIndex without acquiring t.mtx; the caller must
+// already hold t.mtx (read or write). Used by the proof builders, which run
+// under the write lock.
+func (t *Tree) getWithIndexNoLock(key []byte) (int64, []byte) {
 	if t.root == nil {
 		return 0, nil
 	}
@@ -218,6 +250,13 @@ func (t *Tree) GetWithIndex(key []byte) (int64, []byte) {
 func (t *Tree) GetByIndex(index int64) ([]byte, []byte) {
 	t.mtx.RLock()
 	defer t.mtx.RUnlock()
+	return t.getByIndexNoLock(index)
+}
+
+// getByIndexNoLock is GetByIndex without acquiring t.mtx; the caller must
+// already hold t.mtx (read or write). Used by the proof builders, which run
+// under the write lock.
+func (t *Tree) getByIndexNoLock(index int64) ([]byte, []byte) {
 	if t.root == nil {
 		return nil, nil
 	}
@@ -243,6 +282,13 @@ func (t *Tree) Has(key []byte) bool {
 	return t.Get(key) != nil
 }
 
+// hasNoLock is Has without acquiring t.mtx; the caller must already hold
+// t.mtx. Used by getProofNoLock, which runs under the write lock.
+func (t *Tree) hasNoLock(key []byte) bool {
+	_, value := t.getWithIndexNoLock(key)
+	return value != nil
+}
+
 func (t *Tree) Iterator(start, end []byte, ascending bool) dbm.Iterator {
 	t.mtx.RLock()
 	defer t.mtx.RUnlock()
@@ -349,23 +395,38 @@ func nextVersionU32(v uint32, initialVersion uint32) uint32 {
 // GetProof takes a key for creating existence or absence proof and returns the
 // appropriate merkle.Proof. Since this must be called after querying for the value, this function should never error
 // Thus, it will panic on error rather than returning it
+//
+// It takes the write lock for the whole proof build because the traversal
+// reads sibling node hashes via Node.Hash(), which lazily populates
+// MemNode.hash in place. Holding the write lock serializes that mutation
+// against a concurrent commit's RootHash and against Set/Remove, closing the
+// AppHash-divergence race (Immunefi 83246 / STO-601). Internally it uses the
+// *NoLock helpers to avoid recursively re-acquiring t.mtx.
 func (t *Tree) GetProof(key []byte) *ics23.CommitmentProof {
+	t.mtx.Lock()
+	defer t.mtx.Unlock()
+	return t.getProofNoLock(key)
+}
+
+// getProofNoLock is GetProof without acquiring t.mtx; the caller must already
+// hold the write lock.
+func (t *Tree) getProofNoLock(key []byte) *ics23.CommitmentProof {
 	var (
 		commitmentProof *ics23.CommitmentProof
 		err             error
 	)
-	exists := t.Has(key)
+	exists := t.hasNoLock(key)
 
 	if exists {
 		// value was found
-		commitmentProof, err = t.GetMembershipProof(key)
+		commitmentProof, err = t.getMembershipProofNoLock(key)
 		if err != nil {
 			// sanity check: If value was found, membership proof must be creatable
 			panic(fmt.Sprintf("unexpected value for empty proof: %s", err.Error()))
 		}
 	} else {
 		// value wasn't found
-		commitmentProof, err = t.GetNonMembershipProof(key)
+		commitmentProof, err = t.getNonMembershipProofNoLock(key)
 		if err != nil {
 			// sanity check: If value wasn't found, nonmembership proof must be creatable
 			panic(fmt.Sprintf("unexpected error for nonexistence proof: %s", err.Error()))
```

### sei-db/state_db/sc/memiavl/tree_race_test.go
```diff
@@ -0,0 +1,102 @@
+package memiavl
+
+import (
+	"fmt"
+	"sync"
+	"testing"
+
+	"github.com/sei-protocol/sei-chain/sei-db/proto"
+	"github.com/stretchr/testify/require"
+)
+
+// TestTreeProofRaceWithCommit reproduces the Immunefi 83246 / STO-601 race:
+// a latest-height proof query (GetProof) that runs concurrently with a commit
+// (Set + RootHash) used to mutate the shared MemNode.hash cache under a read
+// lock, corrupting the cached internal hashes and diverging the AppHash.
+//
+// With the write-lock fix in RootHash/GetProof this must run clean under
+// `go test -race`.
+func TestTreeProofRaceWithCommit(t *testing.T) {
+	tree := NewEmptyTree(0, 0)
+
+	const seedKeys = 200
+	seed := proto.ChangeSet{}
+	for i := 0; i < seedKeys; i++ {
+		seed.Pairs = append(seed.Pairs, &proto.KVPair{
+			Key:   []byte(fmt.Sprintf("key%05d", i)),
+			Value: []byte(fmt.Sprintf("val%05d", i)),
+		})
+	}
+	tree.ApplyChangeSet(seed)
+	_, _, err := tree.SaveVersion(true)
+	require.NoError(t, err)
+
+	const iterations = 300
+	var wg sync.WaitGroup
+
+	// Writer goroutine: mimics the consensus commit path (mutate + RootHash).
+	wg.Add(1)
+	go func() {
+		defer wg.Done()
+		for i := 0; i < iterations; i++ {
+			tree.ApplyChangeSet(proto.ChangeSet{Pairs: []*proto.KVPair{{
+				Key:   []byte(fmt.Sprintf("key%05d", i%seedKeys)),
+				Value: []byte(fmt.Sprintf("upd%05d", i)),
+			}}})
+			_, _, _ = tree.SaveVersion(true) // calls RootHash internally
+		}
+	}()
+
+	// Reader goroutines: mimic latest-height prove=true ABCI queries plus the
+	// occasional RootHash a query path may trigger.
+	for r := 0; r < 4; r++ {
+		wg.Add(1)
+		go func(r int) {
+			defer wg.Done()
+			for i := 0; i < iterations; i++ {
+				// membership proof for a key known to exist
+				_ = tree.GetProof([]byte(fmt.Sprintf("key%05d", (i*7+r)%seedKeys)))
+				// non-membership proof for a key that never exists
+				_ = tree.GetProof([]byte(fmt.Sprintf("absent%05d", i)))
+				_ = tree.RootHash()
+			}
+		}(r)
+	}
+
+	wg.Wait()
+}
+
+// TestTreeConcurrentRootHash covers concurrent RootHash() calls over a tree
+// whose freshly-inserted nodes still have an empty hash cache, so every caller
+// races to populate MemNode.hash. The digest is deterministic, so all callers
+// must agree and (under -race) must not race.
+func TestTreeConcurrentRootHash(t *testing.T) {
+	tree := NewEmptyTree(0, 0)
+
+	cs := proto.ChangeSet{}
+	for i := 0; i < 500; i++ {
+		cs.Pairs = append(cs.Pairs, &proto.KVPair{
+			Key:   []byte(fmt.Sprintf("k%05d", i)),
+			Value: []byte("v"),
+		})
+	}
+	tree.ApplyChangeSet(cs)
+	// Intentionally do NOT SaveVersion(true) here: leave the node hashes unset
+	// so the concurrent RootHash calls below all attempt the lazy fill.
+
+	const workers = 8
+	var wg sync.WaitGroup
+	hashes := make([][]byte, workers)
+	for i := 0; i < workers; i++ {
+		wg.Add(1)
+		go func(i int) {
+			defer wg.Done()
+			hashes[i] = tree.RootHash()
+		}(i)
+	}
+	wg.Wait()
+
+	for i := 1; i < workers; i++ {
+		require.Equal(t, hashes[0], hashes[i], "concurrent RootHash produced divergent hashes")
+	}
+}
```
