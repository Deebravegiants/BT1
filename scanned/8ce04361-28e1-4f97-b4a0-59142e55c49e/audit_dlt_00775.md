# [?] Fix PebbleDB iterator stack overflow (#3823)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2026-07-29
Source: https://github.com/sei-protocol/sei-chain/commit/0b3eaf37aeb3a00aacdea8f8c7293cc25bdc9235
Type: security-commit

## Details
Fix PebbleDB iterator stack overflow (#3823)

## Summary

Fixes a node crash (`fatal error: stack overflow`) and a silent
wrong-results bug in the
legacy ascending-encoding MVCC iterator (`iterator_ascending.go`), used
by archive nodes
whose PebbleDB state store predates the descending-encoding migration.

Both bugs were already fixed for the descending iterator in #3513. This
applies the same
iterative design to the ascending path, which was missed.

## Bugs fixed

**1. Stack overflow.** `nextForward` / `nextReverse` called themselves
recursively once per
skipped key. A historical query that had to skip many keys (e.g. a
reverse scan at an old
version over a range dominated by newer writes) consumed one stack frame
per key until the
process died. Go cannot `recover()` from a stack overflow, so this took
down the whole node.

**2. Reverse iteration silently dropped keys.** When seeking backwards,
the iterator jumped
past *every* version of a key as soon as the version it landed on was
newer than the query
version — even if that key had an older version that *was* visible.
Affected keys were
missing from historical query results, with no error returned.

Minimal repro: write `keyA@5`, `keyB@30`, `keyA@100`, `keyB@200`, then
reverse-iterate at
version 50. Expected `keyB=B@30, keyA=A@5`; before this change only
`keyA=A@5` was returned.

## Changes

- Replace the recursion in `nextForward` / `nextReverse` with iterative
positioning helpers
(`positionAtOrAfterKey` / `positionAtOrBeforeKey`), mirroring the
descending iterator.
  Stack usage is now O(1) regardless of how many keys a seek skips.
- `seekVisibleVersionForKey` verifies the seek actually landed on the
target key before
accepting it, which is what fixes the dropped-key bug. It also decodes
and re-checks the
version, so malformed entries are skipped rather than reported as
visible.
- Simplify the constructor to use the same positioning helpers instead
of an inline
  version-comparison branch.

No API or on-disk format changes. `nextForward` / `nextReverse` are
private, called only from
`Next()` and the constructor.

## Performance / behavior notes

- **No extra work per query.** The old code performed the same number of
seeks per skipped
key; it just also consumed a stack frame and crashed. This removes the
frame, not the seek.
- The positioning loop is bounded by the number of logical keys
remaining in the iterator's
range and provably advances each iteration (`nextLogicalKey` strictly
increases,
  `prevLogicalKey` strictly decreases), so it terminates.
- Only reverse iteration was returning wrong results; the forward
direction was already
  correct and its test is included as a regression guard.
- Minor: the constructor no longer increments `iterationCount` while
positioning, so the
`iteratorIterations` metric no longer counts construction as an
iteration. This matches
  the descending iterator's behavior.

## Testing

New tests in `iterator_ascending_test.go`, all confirmed to **fail
before** and **pass after**:

- `TestAscendingReverseIteratorDoesNotSkipShadowedKey` — the dropped-key
bug.
- `TestAscendingReverseIteratorDeepSkipDoesNotOverflowStack` — runs in a
child process with a
reduced max stack so the recursion fails fast; reproduces the stack
overflow.
- `TestAscendingIteratorMatchesDescending` — differential test applying
identical randomized
changesets (60 versions, 40 keys, ~1/3 deletions) to one ascending and
one descending DB,
comparing forward and reverse iteration across 5 ranges at 6 query
versions. Fails on the
  first case before the fix.
- `TestAscendingForwardIteratorDoesNotSkipShadowedKey` —
forward-direction guard.

Also verified: full `pebbledb` and `pebbledb/mvcc` suites pass under
`-race`; `gofmt -s`,
`goimports`, and `go vet` clean.

### sei-db/db_engine/pebbledb/mvcc/iterator_ascending.go
```diff
@@ -4,6 +4,7 @@ import (
 	"bytes"
 	"context"
 	"fmt"
+	"math"
 	"sync"
 
 	"github.com/cockroachdb/pebble/v2"
@@ -17,10 +18,11 @@ import (
 )
 
 // This file contains the ascending-version MVCC iterator used for legacy DBs
-// that were written by the pre-descending build. It is a verbatim port of the
-// iterator implementation from main and is intentionally kept isolated from
-// the descending fast-path iterator to avoid subtle interactions between the
-// two encoding schemes.
+// that were written by the pre-descending build. It is kept isolated from the
+// descending fast-path iterator to avoid subtle interactions between the two
+// encoding schemes, but mirrors that iterator's structure: positioning walks
+// logical keys iteratively so stack usage stays constant regardless of how many
+// keys a seek has to skip.
 //
 // Archive nodes that cannot migrate will continue to use this path.
 
@@ -80,27 +82,15 @@ func newAscendingIterator(src *pebble.Iterator, prefix, mvccStart, mvccEnd []byt
 	}
 
 	if valid {
-		currKey, currKeyVersion, ok := SplitMVCCKey(itr.source.Key())
+		currKey, _, ok := SplitMVCCKey(itr.source.Key())
 		if !ok {
 			// XXX: This should not happen as that would indicate we have a malformed MVCC key.
 			panic(fmt.Sprintf("invalid PebbleDB MVCC key: %s", itr.source.Key()))
 		}
-
-		curKeyVersionDecoded, err := decodeUint64Ascending(currKeyVersion)
-		if err != nil {
-			itr.valid = false
-			return itr
-		}
-
-		// We need to check whether initial key iterator visits has a version <= requested version
-		// If larger version, call next to find another key which does
-		if curKeyVersionDecoded > itr.version {
-			itr.Next()
+		if reverse {
+			itr.positionAtOrBeforeKey(currKey)
 		} else {
-			// If version is less, seek to the largest version of that key <= requested iterator version
-			// It is guaranteed this won't move the iterator to a key that is invalid since
-			// curKeyVersionDecoded <= requested iterator version, so there exists at least one version of currKey SeekLT may move to
-			itr.valid = itr.source.SeekLT(MVCCEncodeAscending(currKey, itr.version+1))
+			itr.positionAtOrAfterKey(currKey)
 		}
 	}
 
@@ -120,6 +110,115 @@ func newAscendingIterator(src *pebble.Iterator, prefix, mvccStart, mvccEnd []byt
 	return itr
 }
 
+// visibleVersionUpperBound returns the exclusive SeekLT bound that isolates the
+// versions of key which are visible at itr.version. Ascending encoding sorts a
+// key's versions oldest-first, so this bound sits immediately past the newest
+// visible one. A version of exactly math.MaxInt64 cannot be represented as an
+// exclusive bound and is therefore treated as invisible; versions that large do
+// not occur in practice.
+func (itr *ascendingIterator) visibleVersionUpperBound(key []byte) []byte {
+	version := itr.version
+	if version < math.MaxInt64 {
+		version++
+	}
+	return MVCCEncodeAscending(key, version)
+}
+
+// seekVisibleVersionForKey positions the cursor on the newest version of
+// targetKey that is visible at itr.version, reporting whether such a version
+// exists. When it does not, the seek lands on an earlier logical key, so callers
+// must not assume the cursor still refers to targetKey. The version is decoded
+// and re-checked rather than inferred from the seek bound, so an unparsable
+// version is skipped instead of being reported as visible.
+func (itr *ascendingIterator) seekVisibleVersionForKey(targetKey []byte) bool {
+	if !itr.source.SeekLT(itr.visibleVersionUpperBound(targetKey)) {
+		return false
+	}
+	foundKey, foundVersion, ok := SplitMVCCKey(itr.source.Key())
+	if !ok {
+		return false
+	}
+	if !bytes.Equal(foundKey, targetKey) {
+		return false
+	}
+	foundVersionDecoded, err := decodeUint64Ascending(foundVersion)
+	if err != nil {
+		return false
+	}
+	return foundVersionDecoded <= itr.version
+}
+
+// nextLogicalKey returns the first logical key ordered after every version of
+// currKey. It seeks from an explicit bound rather than stepping the cursor, so
+// it does not depend on where a previous failed seek left the cursor.
+func (itr *ascendingIterator) nextLogicalKey(currKey []byte) ([]byte, bool) {
+	seekKey := MVCCEncodeAscending(currKey, math.MaxInt64)
+	for valid := itr.source.SeekGE(seekKey); valid; valid = itr.source.Next() {
+		nextKey, _, ok := SplitMVCCKey(itr.source.Key())
+		if !ok || !bytes.HasPrefix(nextKey, itr.prefix) {
+			return nil, false
+		}
+		// A key stored at exactly math.MaxInt64 lands on currKey itself; step
+		// over any such residual versions.
+		if !bytes.Equal(nextKey, currKey) {
+			return nextKey, true
+		}
+	}
+	return nil, false
+}
+
+// prevLogicalKey returns the logical key ordered immediately before every
+// version of currKey.
+func (itr *ascendingIterator) prevLogicalKey(currKey []byte) ([]byte, bool) {
+	if !itr.source.SeekLT(MVCCEncodeAscending(currKey, 0)) {
+		return nil, false
+	}
+	prevKey, _, ok := SplitMVCCKey(itr.source.Key())
+	if !ok || !bytes.HasPrefix(prevKey, itr.prefix) {
+		return nil, false
+	}
+	return prevKey, true
+}
+
+// positionAtOrAfterKey walks forward from startKey to the first logical key that
+// is visible at itr.version and not tombstoned. The walk is iterative, so stack
+// usage stays constant no matter how many keys must be skipped.
+func (itr *ascendingIterator) positionAtOrAfterKey(startKey []byte) {
+	currentKey := startKey
+	for {
+		itr.valid = itr.seekVisibleVersionForKey(currentKey)
+		if itr.valid && !itr.cursorTombstoned() {
+			return
+		}
+		nextKey, ok := itr.nextLogicalKey(currentKey)
+		if !ok {
+			itr.valid = false
+			return
+		}
+		currentKey = nextKey
+	}
+}
+
+// positionAtOrBeforeKey walks backward from startKey to the first logical key
+// that is visible at itr.version and not tombstoned. A key whose newest version
+// is above itr.version may still have an older visible version, so the whole key
+// must not be skipped on that basis alone.
+func (itr *ascendingIterator) positionAtOrBeforeKey(startKey []byte) {
+	currentKey := startKey
+	for {
+		itr.valid = itr.seekVisibleVersionForKey(currentKey)
+		if itr.valid && !itr.cursorTombstoned() {
+			return
+		}
+		prevKey, ok := itr.prevLogicalKey(currentKey)
+		if !ok {
+			itr.valid = false
+			return
+		}
+		currentKey = prevKey
+	}
+}
+
 // Domain returns the domain of the iterator. The caller must not modify the
 // return values.
 func (itr *ascendingIterator) Domain() ([]byte, []byte) {
@@ -166,80 +265,12 @@ func (itr *ascendingIterator) nextForward() {
 		panic(fmt.Sprintf("invalid PebbleDB MVCC key: %s", itr.source.Key()))
 	}
 
-	next := itr.source.NextPrefix()
-
-	// First move the iterator to the next prefix, which may not correspond to the
-	// desired version for that key, e.g. if the key was written at a later version,
-	// so we seek back to the latest desired version, s.t. the version is <= itr.version.
-	if next {
-		nextKey, _, ok := SplitMVCCKey(itr.source.Key())
-		if !ok {
-			// XXX: This should not happen as that would indicate we have a malformed
-			// MVCC key.
-			itr.valid = false
-			return
-		}
-		if !bytes.HasPrefix(nextKey, itr.prefix) {
-			// the next key must have itr.prefix as the prefix
-			itr.valid = false
-			return
-		}
-
-		// Move the iterator to the closest version to the desired version, so we
-		// append the current iterator key to the prefix and seek to that key.
-		itr.valid = itr.source.SeekLT(MVCCEncodeAscending(nextKey, itr.version+1))
-
-		tmpKey, tmpKeyVersion, ok := SplitMVCCKey(itr.source.Key())
-		if !ok {
-			// XXX: This should not happen as that would indicate we have a malformed
-			// MVCC key.
-			itr.valid = false
-			return
-		}
-
-		// There exists cases where the SeekLT() call moved us back to the same key
-		// we started at, so we must move to next key, i.e. two keys forward.
-		if bytes.Equal(tmpKey, currKey) {
-			if itr.source.NextPrefix() {
-				itr.nextForward()
-
-				_, tmpKeyVersion, ok = SplitMVCCKey(itr.source.Key())
-				if !ok {
-					// XXX: This should not happen as that would indicate we have a malformed
-					// MVCC key.
-					itr.valid = false
-					return
-				}
-
-			} else {
-				itr.valid = false
-				return
-			}
-		}
-
-		// We need to verify that every Next call either moves the iterator to a key whose version
-		// is less than or equal to requested iterator version, or exhausts the iterator
-		tmpKeyVersionDecoded, err := decodeUint64Ascending(tmpKeyVersion)
-		if err != nil {
-			itr.valid = false
-			return
-		}
-
-		// If iterator is at a entry whose version is higher than requested version, call nextForward again
-		if tmpKeyVersionDecoded > itr.version {
-			itr.nextForward()
-		}
-
-		// The cursor might now be pointing at a key/value pair that is tombstoned.
-		// If so, we must move the cursor.
-		if itr.valid && itr.cursorTombstoned() {
-			itr.nextForward()
-		}
-
+	nextKey, ok := itr.nextLogicalKey(currKey)
+	if !ok {
+		itr.valid = false
 		return
 	}
-
-	itr.valid = false
+	itr.positionAtOrAfterKey(nextKey)
 }
 
 func (itr *ascendingIterator) nextReverse() {
@@ -255,60 +286,12 @@ func (itr *ascendingIterator) nextReverse() {
 		panic(fmt.Sprintf("invalid PebbleDB MVCC key: %s", itr.source.Key()))
 	}
 
-	next := itr.source.SeekLT(MVCCEncodeAscending(currKey, 0))
-
-	// First move the iterator to the next prefix, which may not correspond to the
-	// desired version for that key, e.g. if the key was written at a later version,
-	// so we seek back to the latest desired version, s.t. the version is <= itr.version.
-	if next {
-		nextKey, _, ok := SplitMVCCKey(itr.source.Key())
-		if !ok {
-			// XXX: This should not happen as that would indicate we have a malformed
-			// MVCC key.
-			itr.valid = false
-			return
-		}
-		if !bytes.HasPrefix(nextKey, itr.prefix) {
-			// the next key must have itr.prefix as the prefix
-			itr.valid = false
-			return
-		}
-
-		// Move the iterator to the closest version to the desired version, so we
-		// append the current iterator key to the prefix and seek to that key.
-		itr.valid = itr.source.SeekLT(MVCCEncodeAscending(nextKey, itr.version+1))
-
-		_, tmpKeyVersion, ok := SplitMVCCKey(itr.source.Key())
-		if !ok {
-			// XXX: This should not happen as that would indicate we have a malformed
-			// MVCC key.
-			itr.valid = false
-			return
-		}
-
-		// We need to verify that every Next call either moves the iterator to a key whose version
-		// is less than or equal to requested iterator version, or exhausts the iterator
-		tmpKeyVersionDecoded, err := decodeUint64Ascending(tmpKeyVersion)
-		if err != nil {
-			itr.valid = false
-			return
-		}
-
-		// If iterator is at a entry whose version is higher than requested version, call nextReverse again
-		if tmpKeyVersionDecoded > itr.version {
-			itr.nextReverse()
-		}
-
-		// The cursor might now be pointing at a key/value pair that is tombstoned.
-		// If so, we must move the cursor.
-		if itr.valid && itr.cursorTombstoned() {
-			itr.nextReverse()
-		}
-
+	prevKey, ok := itr.prevLogicalKey(currKey)
+	if !ok {
+		itr.valid = false
 		return
 	}
-
-	itr.valid = false
+	itr.positionAtOrBeforeKey(prevKey)
 }
 
 func (itr *ascendingIterator) Next() {
```

### sei-db/db_engine/pebbledb/mvcc/iterator_ascending_test.go
```diff
@@ -0,0 +1,244 @@
+package mvcc
+
+import (
+	"fmt"
+	"math/rand"
+	"os"
+	"os/exec"
+	"runtime/debug"
+	"strings"
+	"testing"
+
+	"github.com/cockroachdb/pebble/v2"
+	"github.com/stretchr/testify/require"
+
+	dbm "github.com/tendermint/tm-db"
+
+	"github.com/sei-protocol/sei-chain/sei-db/config"
+	"github.com/sei-protocol/sei-chain/sei-db/proto"
+)
+
+const ascIterTestStore = "store1"
+
+// newAscendingIterTestDB seeds a directory the way the legacy ascending-version
+// build would have left it -- ascending-encoded data plus a latest-version
+// marker, but no descending sentinel -- so OpenDB selects the ascending path.
+func newAscendingIterTestDB(t *testing.T) *Database {
+	t.Helper()
+
+	dir := t.TempDir()
+	raw, err := pebble.Open(dir, &pebble.Options{Comparer: MVCCComparer})
+	require.NoError(t, err)
+	// Seeded under a different store so it never shows up in the iterations below.
+	require.NoError(t, raw.Set(
+		MVCCEncodeAscending(prependStoreKey("seedstore", []byte("seed")), 1),
+		MVCCEncodeAscending([]byte("seed"), 0),
+		pebble.Sync,
+	))
+	var ts [VersionSize]byte
+	ts[0] = 1
+	require.NoError(t, raw.Set([]byte(latestVersionKey), ts[:], pebble.Sync))
+	require.NoError(t, raw.Close())
+
+	cfg := config.DefaultStateStoreConfig()
+	cfg.Backend = "pebbledb"
+	store, err := OpenDB(dir, cfg)
+	require.NoError(t, err)
+	db := store.(*Database)
+	t.Cleanup(func() { _ = db.Close() })
+	require.False(t, db.descending, "seeded legacy DB must open in ascending mode")
+	return db
+}
+
+// A logical key that is visible at the target version but was also written at a
+// later version must still be returned by a reverse iteration at that version.
+// The previous implementation seeked past every version of such a key as soon as
+// the version it landed on was newer than the target, dropping the key entirely.
+func TestAscendingReverseIteratorDoesNotSkipShadowedKey(t *testing.T) {
+	db := newAscendingIterTestDB(t)
+
+	applyVersion(t, db, ascIterTestStore, 5, []byte("keyA"), []byte("A@5"))
+	applyVersion(t, db, ascIterTestStore, 30, []byte("keyB"), []byte("B@30"))
+	applyVersion(t, db, ascIterTestStore, 100, []byte("keyA"), []byte("A@100"))
+	applyVersion(t, db, ascIterTestStore, 200, []byte("keyB"), []byte("B@200"))
+
+	itr, err := db.ReverseIterator(ascIterTestStore, 50, nil, nil)
+	require.NoError(t, err)
+	defer func() { _ = itr.Close() }()
+
+	var got []string
+	for ; itr.Valid(); itr.Next() {
+		got = append(got, fmt.Sprintf("%s=%s", itr.Key(), itr.Value()))
+	}
+	require.NoError(t, itr.Error())
+	require.Equal(t, []string{"keyB=B@30", "keyA=A@5"}, got)
+}
+
+// The same shadowing case in the forward direction.
+func TestAscendingForwardIteratorDoesNotSkipShadowedKey(t *testing.T) {
+	db := newAscendingIterTestDB(t)
+
+	applyVersion(t, db, ascIterTestStore, 5, []byte("keyA"), []byte("A@5"))
+	applyVersion(t, db, ascIterTestStore, 30, []byte("keyB"), []byte("B@30"))
+	applyVersion(t, db, ascIterTestStore, 100, []byte("keyA"), []byte("A@100"))
+	applyVersion(t, db, ascIterTestStore, 200, []byte("keyB"), []byte("B@200"))
+
+	itr, err := db.Iterator(ascIterTestStore, 50, nil, nil)
+	require.NoError(t, err)
+	defer func() { _ = itr.Close() }()
+
+	var got []string
+	for ; itr.Valid(); itr.Next() {
+		got = append(got, fmt.Sprintf("%s=%s", itr.Key(), itr.Value()))
+	}
+	require.NoError(t, itr.Error())
+	require.Equal(t, []string{"keyA=A@5", "keyB=B@30"}, got)
+}
+
+// Reverse iteration at an old version must not consume stack proportional to the
+// number of keys it has to skip. The child process runs with a small max stack so
+// that a per-skipped-key stack frame fails fast instead of needing millions of
+// keys to exhaust the default limit.
+func TestAscendingReverseIteratorDeepSkipDoesNotOverflowStack(t *testing.T) {
+	if os.Getenv("MVCC_ASC_DEEP_SKIP_CHILD") == "1" {
+		debug.SetMaxStack(16 << 20)
+		runAscendingDeepReverseSkip(t)
+		return
+	}
+
+	cmd := exec.Command(os.Args[0], "-test.run=TestAscendingReverseIteratorDeepSkipDoesNotOverflowStack", "-test.v")
+	cmd.Env = append(os.Environ(), "MVCC_ASC_DEEP_SKIP_CHILD=1")
+	out, err := cmd.CombinedOutput()
+	if err != nil {
+		t.Fatalf("child process failed: %v\nstack overflow present: %v\n%s",
+			err, strings.Contains(string(out), "stack overflow"), lastLinesOfOutput(string(out), 40))
+	}
+}
+
+func runAscendingDeepReverseSkip(t *testing.T) {
+	db := newAscendingIterTestDB(t)
+
+	// One key visible at version 10, then many keys that sort after it and only
+	// exist at much later versions, all of which a reverse scan at 10 must skip.
+	applyVersion(t, db, ascIterTestStore, 10, []byte("aaa"), []byte("visible"))
+
+	const newKeys = 150_000
+	const batch = 1000
+	for i := 0; i < newKeys; i += batch {
+		pairs := make([]*proto.KVPair, 0, batch)
+		for j := 0; j < batch; j++ {
+			pairs = append(pairs, &proto.KVPair{
+				Key:   []byte(fmt.Sprintf("zzz%08d", i+j)),
+				Value: []byte("new"),
+			})
+		}
+		require.NoError(t, db.ApplyChangesetSync(int64(1000+i/batch), []*proto.NamedChangeSet{{
+			Name:      ascIterTestStore,
+			Changeset: proto.ChangeSet{Pairs: pairs},
+		}}))
+	}
+
+	itr, err := db.ReverseIterator(ascIterTestStore, 10, nil, nil)
+	require.NoError(t, err)
+	defer func() { _ = itr.Close() }()
+
+	var got []string
+	for ; itr.Valid(); itr.Next() {
+		got = append(got, fmt.Sprintf("%s=%s", itr.Key(), itr.Value()))
+	}
+	require.NoError(t, itr.Error())
+	require.Equal(t, []string{"aaa=visible"}, got)
+}
+
+// The ascending iterator must agree with the descending iterator, which is the
+// primary path for all new DBs. Identical changesets are applied to one DB of
+// each encoding and every iteration is compared, covering multi-version keys,
+// tombstones, resurrected keys and bounded ranges at several query versions.
+func TestAscendingIteratorMatchesDescending(t *testing.T) {
+	asc := newAscendingIterTestDB(t)
+	desc := newTestDB(t, false)
+	require.True(t, desc.descending, "fresh DB must open in descending mode")
+
+	rng := rand.New(rand.NewSource(20260728))
+	keys := make([][]byte, 0, 40)
+	for i := 0; i < 40; i++ {
+		keys = append(keys, []byte(fmt.Sprintf("key%03d", i)))
+	}
+
+	const versions = 60
+	for v := int64(1); v <= versions; v++ {
+		pairs := make([]*proto.KVPair, 0, 8)
+		for n := 0; n < 1+rng.Intn(6); n++ {
+			k := keys[rng.Intn(len(keys))]
+			// Roughly a third of writes are deletions, so tombstones interleave
+			// with live versions of the same logical key.
+			if rng.Intn(3) == 0 {
+				pairs = append(pairs, &proto.KVPair{Key: k, Delete: true})
+				continue
+			}
+			pairs = append(pairs, &proto.KVPair{
+				Key:   k,
+				Value: []byte(fmt.Sprintf("v%d@%d", rng.Intn(1000), v)),
+			})
+		}
+		cs := []*proto.NamedChangeSet{{
+			Name:      ascIterTestStore,
+			Changeset: proto.ChangeSet{Pairs: pairs},
+		}}
+		require.NoError(t, asc.ApplyChangesetSync(v, cs))
+		require.NoError(t, desc.ApplyChangesetSync(v, cs))
+	}
+
+	ranges := []struct {
+		name       string
+		start, end []byte
+	}{
+		{"full", nil, nil},
+		{"bounded", []byte("key005"), []byte("key030")},
+		{"start-only", []byte("key020"), nil},
+		{"end-only", nil, []byte("key010")},
+		{"empty", []byte("key900"), nil},
+	}
+
+	for _, queryVersion := range []int64{1, 7, 23, 42, versions, versions + 5} {
+		for _, r := range ranges {
+			for _, reverse := range []bool{false, true} {
+				name := fmt.Sprintf("v%d/%s/reverse=%v", queryVersion, r.name, reverse)
+				gotAsc := collectIteration(t, asc, queryVersion, r.start, r.end, reverse)
+				gotDesc := collectIteration(t, desc, queryVersion, r.start, r.end, reverse)
+				require.Equal(t, gotDesc, gotAsc, "ascending/descending mismatch at %s", name)
+			}
+		}
+	}
+}
+
+func collectIteration(t *testing.T, db *Database, version int64, start, end []byte, reverse bool) []string {
+	t.Helper()
+
+	var (
+		itr dbm.Iterator
+		err error
+	)
+	if reverse {
+		itr, err = db.ReverseIterator(ascIterTestStore, version, start, end)
+	} else {
+		itr, err = db.Iterator(ascIterTestStore, version, start, end)
+	}
+	require.NoError(t, err)
+	defer func() { _ = itr.Close() }()
+
+	got := []string{}
+	for ; itr.Valid(); itr.Next() {
+		got = append(got, fmt.Sprintf("%s=%s", itr.Key(), itr.Value()))
+	}
+	require.NoError(t, itr.Error())
+	return got
+}
+
+func lastLinesOfOutput(s string, n int) string {
+	lines := strings.Split(strings.TrimRight(s, "\n"), "\n")
+	if len(lines) > n {
+		lines = lines[len(lines)-n:]
+	}
+	return strings.Join(lines, "\n")
+}
```
