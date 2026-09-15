# [?] commitment: fix warmuper arena data race in HashSort (#21432)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-06-09
Source: https://github.com/erigontech/erigon/commit/c15f43363c28f091218ee3803d1992b6321f5c70
Type: security-commit

## Details
commitment: fix warmuper arena data race in HashSort (#21432)

## Problem

`HashSort` streams each batch's hashed/plain keys into a reused
`byteArena` bump buffer and hands every key to the async warmuper as a
sub-slice for MDBX prefetch. At each 10k batch boundary it reset that
single arena while warmup workers were still reading earlier keys — the
next batch's `arenaAlloc` overwrote bytes a worker was mid-read on. Data
race.

Latent on main: `HexToCompact` tolerates the garbage (at worst a wasted
prefetch). On nibblesv2 (#21146) `EncodeKeyV2` validates nibbles and
panics on the corrupted byte: `panic: nibbles v2: nibble at index 68 is
0xff`, mainnet ~blk 24.83M, mid commitment.

## Fix

Replace the single arena with a 2-slot ring (`arenaRingSize`) keyed by a
generation counter. Each warmed key is tagged with the current `gen`;
the warmuper keeps a per-slot in-flight count (`outstanding[gen %
ringSize]`). Before a batch boundary reuses a slot, the producer calls
`WaitBufferFree(slot)`, which blocks until that slot's
previous-generation warm items have drained — so no worker still
references the bytes about to be overwritten. Workers decrement on
completion and broadcast on drain-to-zero; a waker goroutine releases
any waiter on ctx cancellation.

Zero-copy, no per-key allocation: the arena is pre-sized once per batch
(`arenaEnsureCap`), and an over-capacity key falls back to an
independent allocation rather than reallocating the buffer (which would
invalidate live sub-slices). Wired at both `HashSort` batch boundaries
for `ModeDirect` and `ModeUpdate`; the `nil`-warmuper path is unchanged.

## Tests

- `TestHashSort_WarmupArenaNoRace` — `-race` repro; DATA RACE in
`HexToCompact` on the old single-arena wiring, green after. Covers
`ModeDirect` and `ModeUpdate`.
- `WaitBufferFree` behaviour: blocks until a straggler drains, fast-path
when the slot is already empty, unblocks on ctx cancel.
- Slot-reuse invariant `curArena == gen % arenaRingSize` survives a
cancel landing inside a boundary wait; `arenaAlloc` returns
non-overlapping sub-slices and falls back cleanly on over-capacity.

`make lint` clean, `make erigon integration` builds, commitment package
green under `-race`.

---------

Co-authored-by: Alex Sharov <AskAlexSharov@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

### execution/commitment/commitment.go
```diff
@@ -1457,36 +1457,46 @@ type Updates struct {
 	nibbles       [16]*etl.Collector
 
 	batchSlab []KeyUpdate // grow-only slab for HashSort batch (avoids per-key heap allocs)
-	byteArena []byte      // grow-only byte arena for HashSort key copies
+
+	// Ring of byte arenas for HashSort key copies; a slot is reused only after its prior generation's warm items drain.
+	arenas   [arenaRingSize][]byte
+	curArena int
+	gen      uint64
 }
 
+// arenaRingSize is how many byte arenas HashSort cycles; raising it only adds memory headroom, never affects correctness.
+const arenaRingSize = 2
+
 // arenaAlloc appends b to the byte arena and returns the sub-slice.
 // The returned slice is valid until the arena is reset.
 // The arena must have sufficient capacity (via arenaEnsureCap) before
 // accumulating a batch; if capacity is exceeded, arenaAlloc falls back
 // to an independent heap allocation to keep previously returned
 // sub-slices valid.
 func (t *Updates) arenaAlloc(b []byte) []byte {
-	off := len(t.byteArena)
+	arena := t.arenas[t.curArena]
+	off := len(arena)
 	needed := off + len(b)
-	if needed > cap(t.byteArena) {
+	if needed > cap(arena) {
 		// Arena capacity exceeded — fall back to an independent allocation.
 		// This keeps previously returned sub-slices valid while avoiding a
 		// panic that would crash a production node.
 		result := make([]byte, len(b))
 		copy(result, b)
 		return result
 	}
-	t.byteArena = t.byteArena[:needed]
-	copy(t.byteArena[off:], b)
-	return t.byteArena[off:needed]
+	arena = arena[:needed]
+	copy(arena[off:], b)
+	t.arenas[t.curArena] = arena
+	return arena[off:needed]
 }
 
-// arenaEnsureCap ensures the byte arena has at least cap bytes of capacity.
-// Must be called before each batch to prevent mid-batch reallocation.
+// arenaEnsureCap reserves at least c bytes in every ring buffer; call before a batch so a mid-batch grow can't reallocate and invalidate returned sub-slices.
 func (t *Updates) arenaEnsureCap(c int) {
-	if cap(t.byteArena) < c {
-		t.byteArena = make([]byte, 0, c)
+	for i := range t.arenas {
+		if cap(t.arenas[i]) < c {
+			t.arenas[i] = make([]byte, 0, c)
+		}
 	}
 }
 
@@ -1811,12 +1821,14 @@ func (t *Updates) HashSort(ctx context.Context, warmuper *Warmuper, fn func(hk,
 		clear(t.keys)
 
 		t.batchSlab = t.batchSlab[:0]
-		// Pre-allocate arena to avoid mid-batch reallocation that would
-		// invalidate previously returned sub-slices (hk/pk in batchSlab).
-		// Worst case: storage keys produce 128-byte nibblized hashed keys +
-		// 52-byte plain keys = 180 bytes/key. Use 192 with headroom.
+		if warmuper != nil {
+			if err := warmuper.WaitBufferFree(t.curArena); err != nil {
+				return err
+			}
+		}
+		// Pre-size the arena so a mid-batch grow can't reallocate and invalidate live sub-slices (≤180 B/key, 192 with headroom).
 		t.arenaEnsureCap(hashSortBatchSize * 192)
-		t.byteArena = t.byteArena[:0]
+		t.arenas[t.curArena] = t.arenas[t.curArena][:0]
 		var prevKey []byte
 
 		err := t.etl.Load(nil, "", func(k, v []byte, table etl.CurrentTableReader, next etl.LoadNextFunc) error {
@@ -1838,7 +1850,7 @@ func (t *Updates) HashSort(ctx context.Context, warmuper *Warmuper, fn func(hk,
 						startDepth++
 					}
 				}
-				warmuper.WarmKey(hk, startDepth)
+				warmuper.WarmKey(hk, startDepth, t.gen)
 				prevKey = append(prevKey[:0], hk...)
 			}
 
@@ -1854,11 +1866,17 @@ func (t *Updates) HashSort(ctx context.Context, warmuper *Warmuper, fn func(hk,
 						return err
 					}
 				}
+				t.batchSlab = t.batchSlab[:0]
+				nextGen := t.gen + 1
+				slot := int(nextGen % arenaRingSize)
 				if warmuper != nil {
-					warmuper.DrainPending()
+					if err := warmuper.WaitBufferFree(slot); err != nil {
+						return err
+					}
 				}
-				t.batchSlab = t.batchSlab[:0]
-				t.byteArena = t.byteArena[:0]
+				t.gen = nextGen
+				t.arenas[slot] = t.arenas[slot][:0]
+				t.curArena = slot
 			}
 			return nil
 		}, etl.TransformArgs{Quit: ctx.Done()})
@@ -1882,8 +1900,13 @@ func (t *Updates) HashSort(ctx context.Context, warmuper *Warmuper, fn func(hk,
 
 	case ModeUpdate:
 		t.batchSlab = t.batchSlab[:0]
+		if warmuper != nil {
+			if err := warmuper.WaitBufferFree(t.curArena); err != nil {
+				return err
+			}
+		}
 		t.arenaEnsureCap(hashSortBatchSize * 144)
-		t.byteArena = t.byteArena[:0]
+		t.arenas[t.curArena] = t.arenas[t.curArena][:0]
 		var prevKey []byte
 		var processErr error
 
@@ -1906,7 +1929,7 @@ func (t *Updates) HashSort(ctx context.Context, warmuper *Warmuper, fn func(hk,
 						startDepth++
 					}
 				}
-				warmuper.WarmKey(hk, startDepth)
+				warmuper.WarmKey(hk, startDepth, t.gen)
 				prevKey = append(prevKey[:0], hk...)
 			}
 
@@ -1923,11 +1946,18 @@ func (t *Updates) HashSort(ctx context.Context, warmuper *Warmuper, fn func(hk,
 						return false
 					}
 				}
+				t.batchSlab = t.batchSlab[:0]
+				nextGen := t.gen + 1
+				slot := int(nextGen % arenaRingSize)
 				if warmuper != nil {
-					warmuper.DrainPending()
+					if err := warmuper.WaitBufferFree(slot); err != nil {
+						processErr = err
+						return false
+					}
 				}
-				t.batchSlab = t.batchSlab[:0]
-				t.byteArena = t.byteArena[:0]
+				t.gen = nextGen
+				t.arenas[slot] = t.arenas[slot][:0]
+				t.curArena = slot
 			}
 			return true
 		})
@@ -1971,7 +2001,11 @@ func (t *Updates) Reset() {
 	default:
 	}
 	t.batchSlab = t.batchSlab[:0]
-	t.byteArena = t.byteArena[:0]
+	for i := range t.arenas {
+		t.arenas[i] = t.arenas[i][:0]
+	}
+	t.curArena = 0
+	t.gen = 0
 }
 
 type KeyUpdate struct {
```

### execution/commitment/commitment_test.go
```diff
@@ -25,7 +25,9 @@ import (
 	"math/bits"
 	"math/rand"
 	"sort"
+	"sync/atomic"
 	"testing"
+	"time"
 
 	"github.com/stretchr/testify/require"
 
@@ -48,6 +50,425 @@ func noopCtxFactory() (PatriciaContext, func()) {
 	return &noopPatriciaContext{}, nil
 }
 
+// gatedPatriciaContext is a mock PatriciaContext with a controllable in-flight window:
+// sleep+descend keep a worker re-reading its arena-backed key across batch boundaries,
+// while entered/release gate a worker inside Branch for deterministic ordering.
+type gatedPatriciaContext struct {
+	sleep    time.Duration
+	descend  bool
+	entered  chan struct{}
+	release  chan struct{}
+	gateDone atomic.Bool
+}
+
+func (g *gatedPatriciaContext) Branch(prefix []byte) ([]byte, kv.Step, error) {
+	// Gate only the first Branch call so a released worker can't wedge re-sending to entered.
+	if (g.entered != nil || g.release != nil) && !g.gateDone.Swap(true) {
+		if g.entered != nil {
+			g.entered <- struct{}{}
+		}
+		if g.release != nil {
+			<-g.release
+		}
+	}
+	if g.sleep > 0 {
+		time.Sleep(g.sleep)
+	}
+	if g.descend {
+		// touch map + bitmap 0x0001 (child nibble 0) + fieldBits 0x00: warmupKey
+		// descends on nibble 0, re-reading hashedKey at every level.
+		return []byte{0, 0, 0, 1, 0, 0}, 0, nil
+	}
+	return []byte{0, 0, 0, 0}, 0, nil
+}
+
+func (g *gatedPatriciaContext) PutBranch(prefix, data, prevData []byte) error { return nil }
+func (g *gatedPatriciaContext) Account(plainKey []byte) (*Update, error)      { return nil, nil }
+func (g *gatedPatriciaContext) Storage(plainKey []byte) (*Update, error)      { return nil, nil }
+func (g *gatedPatriciaContext) TxNum() uint64                                 { return 0 }
+
+// slowCtxFactory makes the first worker a slow straggler that holds one key across many
+// batch resets while the rest run fast, so the producer's arena reset races its in-flight reads.
+func slowCtxFactory(stall time.Duration) TrieContextFactory {
+	var n atomic.Int32
+	return func() (PatriciaContext, func()) {
+		if n.Add(1) == 1 {
+			return &gatedPatriciaContext{sleep: stall, descend: true}, nil
+		}
+		return &gatedPatriciaContext{}, nil
+	}
+}
+
+// gatedCtxFactory returns a factory whose contexts signal entered then block on
+// release inside Branch, for deterministic single-worker ordering tests.
+func gatedCtxFactory(entered, release chan struct{}) TrieContextFactory {
+	return func() (PatriciaContext, func()) {
+		return &gatedPatriciaContext{entered: entered, release: release}, nil
+	}
+}
+
+// genNibbleKeys produces n unique keyLen-byte keys whose every byte is a valid nibble
+// (0x00-0x0F), with the index encoded in the trailing nibbles so keys are distinct.
+func genNibbleKeys(n, keyLen int) [][]byte {
+	keys := make([][]byte, n)
+	for i := 0; i < n; i++ {
+		k := make([]byte, keyLen)
+		v := i
+		for j := keyLen - 1; j >= 0; j-- {
+			k[j] = byte(v & 0x0F)
+			v >>= 4
+		}
+		keys[i] = k
+	}
+	return keys
+}
+
+// TestHashSort_WarmupArenaNoRace reproduces the arena data race: at a batch boundary HashSort
+// resets a buffer while warmup workers still read key slices aliasing it. -race is the signal.
+func TestHashSort_WarmupArenaNoRace(t *testing.T) {
+	t.Parallel()
+
+	const numKeys = 20_000 // two batches: one in-loop arena reset mid-stream plus the final batch
+	const keyLen = 64
+
+	for _, mode := range []Mode{ModeDirect, ModeUpdate} {
+		name := "ModeDirect"
+		if mode == ModeUpdate {
+			name = "ModeUpdate"
+		}
+		t.Run(name, func(t *testing.T) {
+			ut := NewUpdates(mode, t.TempDir(), keyHasherNoop)
+			for _, k := range genNibbleKeys(numKeys, keyLen) {
+				ut.TouchPlainKey(string(k), []byte("v"), ut.TouchStorage)
+			}
+			require.EqualValues(t, numKeys, ut.Size())
+
+			ctx := context.Background()
+			warmuper := NewWarmuper(ctx, WarmupConfig{
+				Enabled: true,
+				// Large per-level stall keeps the straggler in-flight across the arena reset.
+				CtxFactory: slowCtxFactory(2 * time.Millisecond),
+				NumWorkers: 4,
+				MaxDepth:   64,
+				LogPrefix:  "test",
+			})
+			warmuper.Start()
+
+			visited := 0
+			err := ut.HashSort(ctx, warmuper, func(hk, pk []byte, _ *Update) error {
+				visited++
+				return nil
+			})
+			require.NoError(t, err)
+			require.Equal(t, numKeys, visited)
+			require.NoError(t, warmuper.Wait())
+		})
+	}
+}
+
+// TestHashSort_NilWarmuper exercises the nil-warmuper batch-boundary path (the else branch
+// that resets the arena directly), crossing the in-loop reset for both modes.
+func TestHashSort_NilWarmuper(t *testing.T) {
+	t.Parallel()
+
+	const numKeys = 20_000
+	const keyLen = 64
+
+	for _, mode := range []Mode{ModeDirect, ModeUpdate} {
+		name := "ModeDirect"
+		if mode == ModeUpdate {
+			name = "ModeUpdate"
+		}
+		t.Run(name, func(t *testing.T) {
+			ut := NewUpdates(mode, t.TempDir(), keyHasherNoop)
+			for _, k := range genNibbleKeys(numKeys, keyLen) {
+				ut.TouchPlainKey(string(k), []byte("v"), ut.TouchStorage)
+			}
+			require.EqualValues(t, numKeys, ut.Size())
+
+			visited := 0
+			err := ut.HashSort(context.Background(), nil, func(hk, pk []byte, _ *Update) error {
+				visited++
+				return nil
+			})
+			require.NoError(t, err)
+			require.Equal(t, numKeys, visited)
+		})
+	}
+}
+
+// TestHashSort_WarmupLap crosses ≥3 batch boundaries (K=2) so a ring slot is reused while a slow
+// straggler still holds a key from that slot's previous generation; the producer must block in
+// WaitBufferFree until it drains. -race is the signal.
+func TestHashSort_WarmupLap(t *testing.T) {
+	t.Parallel()
+
+	const numKeys = 30_000 // three batch boundaries → gen reaches 3, so each ring slot is reused
+	const keyLen = 64
+
+	for _, mode := range []Mode{ModeDirect, ModeUpdate} {
+		name := "ModeDirect"
+		if mode == ModeUpdate {
+			name = "ModeUpdate"
+		}
+		t.Run(name, func(t *testing.T) {
+			ut := NewUpdates(mode, t.TempDir(), keyHasherNoop)
+			for _, k := range genNibbleKeys(numKeys, keyLen) {
+				ut.TouchPlainKey(string(k), []byte("v"), ut.TouchStorage)
+			}
+			require.EqualValues(t, numKeys, ut.Size())
+
+			ctx := context.Background()
+			warmuper := NewWarmuper(ctx, WarmupConfig{
+				Enabled:    true,
+				CtxFactory: slowCtxFactory(2 * time.Millisecond),
+				NumWorkers: 4,
+				MaxDepth:   64,
+				LogPrefix:  "test",
+			})
+			warmuper.Start()
+
+			visited := 0
+			err := ut.HashSort(ctx, warmuper, func(hk, pk []byte, _ *Update) error {
+				visited++
+				return nil
+			})
+			require.NoError(t, err)
+			require.Equal(t, numKeys, visited)
+			// gen advances once per batch boundary; ≥3 means at least one ring slot was
+			// reused (lapped) — the path WaitBufferFree guards.
+			require.GreaterOrEqual(t, ut.gen, uint64(3))
+			require.NoError(t, warmuper.Wait())
+		})
+	}
+}
+
+// gatedStragglerFactory makes the first worker block inside Branch on release (holding its
+// first key) while every other worker runs fast, so exactly one ring slot stays occupied.
+func gatedStragglerFactory(entered, release chan struct{}) TrieContextFactory {
+	var n atomic.Int32
+	return func() (PatriciaContext, func()) {
+		if n.Add(1) == 1 {
+			return &gatedPatriciaContext{entered: entered, release: release}, nil
+		}
+		return &gatedPatriciaContext{}, nil
+	}
+}
+
+// TestHashSort_WaitBufferFreeErrorKeepsArenaInvariant cancels the context during a boundary
+// WaitBufferFree while a straggler pins the slot, asserting the curArena == gen % arenaRingSize
+// invariant survives the error return.
+func TestHashSort_WaitBufferFreeErrorKeepsArenaInvariant(t *testing.T) {
+	t.Parallel()
+
+	const numKeys = 30_000 // ≥3 batch boundaries so a ring slot is reused (lapped)
+	const keyLen = 64
+	const lapFnCall = 2 * hashSortBatchSize // fn calls for gen 0 + gen 1, completing right before boundary 2
+
+	for _, mode := range []Mode{ModeDirect, ModeUpdate} {
+		name := "ModeDirect"
+		if mode == ModeUpdate {
+			name = "ModeUpdate"
+		}
+		t.Run(name, func(t *testing.T) {
+			ut := NewUpdates(mode, t.TempDir(), keyHasherNoop)
+			for _, k := range genNibbleKeys(numKeys, keyLen) {
+				ut.TouchPlainKey(string(k), []byte("v"), ut.TouchStorage)
+			}
+
+			ctx, cancel := context.WithCancel(context.Background())
+			defer cancel()
+			entered := make(chan struct{}, 1)
+			release := make(chan struct{})
+			warmuper := NewWarmuper(ctx, WarmupConfig{
+				Enabled:    true,
+				CtxFactory: gatedStragglerFactory(entered, release),
+				NumWorkers: 4,
+				MaxDepth:   64,
+				LogPrefix:  "test",
+			})
+			warmuper.Start()
+			defer warmuper.CloseAndWait()
+			defer close(release)
+
+			// fn runs only on the producer goroutine, so this counter is race-free. Signaling at
+			// lapFnCall (right before the gen++/WaitBufferFree block) makes the cancel land inside the wait.
+			fnCalls := 0
+			reachedLap := make(chan struct{})
+			errCh := make(chan error, 1)
+			go func() {
+				errCh <- ut.HashSort(ctx, warmuper, func(hk, pk []byte, _ *Update) error {
+					fnCalls++
+					if fnCalls == lapFnCall {
+						close(reachedLap)
+					}
+					return nil
+				})
+			}()
+
+			<-entered // the straggler holds a gen-0 key, pinning slot 0
+			require.GreaterOrEqual(t, warmuper.outstanding[0].Load(), int64(1))
+
+			<-reachedLap // batch-2 fn-loop done; producer heads into WaitBufferFree(0), which slot 0 pins
+			cancel()
+
+			select {
+			case err := <-errCh:
+				require.Error(t, err)
+			case <-time.After(2 * time.Second):
+				t.Fatal("HashSort did not return after cancellation")
+			}
+
+			require.Equal(t, int(ut.gen%arenaRingSize), ut.curArena)
+		})
+	}
+}
+
+// TestUpdates_ArenaAlloc verifies that sequential allocations within a ring buffer return
+// non-overlapping sub-slices, and that an over-capacity request falls back to an independent
+// allocation that leaves prior sub-slices intact.
+func TestUpdates_ArenaAlloc(t *testing.T) {
+	t.Parallel()
+
+	ut := NewUpdates(ModeDirect, t.TempDir(), keyHasherNoop)
+	ut.arenaEnsureCap(16)
+
+	a := ut.arenaAlloc([]byte("aaaa"))
+	b := ut.arenaAlloc([]byte("bbbb"))
+	require.Equal(t, []byte("aaaa"), a)
+	require.Equal(t, []byte("bbbb"), b)
+
+	// Sub-slices are contiguous and non-overlapping within the same buffer.
+	require.Equal(t, &ut.arenas[ut.curArena][0], &a[0])
+	require.Equal(t, &ut.arenas[ut.curArena][4], &b[0])
+
+	// Mutating the second slice must not touch the first.
+	b[0] = 'X'
+	require.Equal(t, []byte("aaaa"), a)
+
+	// Over-capacity request falls back to an independent allocation; prior slices stay valid.
+	big := ut.arenaAlloc(bytes.Repeat([]byte("z"), 32))
+	require.Equal(t, bytes.Repeat([]byte("z"), 32), big)
+	require.Equal(t, []byte("aaaa"), a)
+	require.Equal(t, []byte("Xbbb"), b)
+	// The fallback slice is not backed by the current ring buffer.
+	require.NotEqual(t, &ut.arenas[ut.curArena][0], &big[0])
+}
+
+// TestWarmuper_WaitBufferFree_BlocksUntilStragglerDone verifies that WaitBufferFree
+// blocks while a warm item for the slot's generation is still in-flight, and returns
+// once that item completes (slot drains to zero).
+func TestWarmuper_WaitBufferFree_BlocksUntilStragglerDone(t *testing.T) {
+	t.Parallel()
+
+	entered := make(chan struct{})
+	release := make(chan struct{})
+	warmuper := NewWarmuper(context.Background(), WarmupConfig{
+		Enabled:    true,
+		CtxFactory: gatedCtxFactory(entered, release),
+		NumWorkers: 1,
+		MaxDepth:   64,
+		LogPrefix:  "test",
+	})
+	warmuper.Start()
+	defer func() { require.NoError(t, warmuper.Wait()) }()
+
+	warmuper.WarmKey([]byte{0, 1, 2, 3}, 0, 0)
+	<-entered // worker is now inside Branch, key for gen 0 in-flight
+	require.Equal(t, int64(1), warmuper.outstanding[0].Load())
+
+	done := make(chan struct{})
+	go func() {
+		_ = warmuper.WaitBufferFree(0)
+		close(done)
+	}()
+
+	select {
+	case <-done:
+		t.Fatal("WaitBufferFree returned while a gen-0 item is still in-flight")
+	case <-time.After(50 * time.Millisecond):
+	}
+
+	close(release) // let the worker finish
+
+	select {
+	case <-done:
+	case <-time.After(2 * time.Second):
+		t.Fatal("WaitBufferFree did not return after the straggler drained")
+	}
+	require.Equal(t, int64(0), warmuper.outstanding[0].Load())
+}
+
+// TestWarmuper_WaitBufferFree_UnblocksOnCancel verifies a producer parked in WaitBufferFree wakes
+// and returns the context error when the warmuper is canceled while a counted item is stuck.
+func TestWarmuper_WaitBufferFree_UnblocksOnCancel(t *testing.T) {
+	t.Parallel()
+
+	ctx, cancel := context.WithCancel(context.Background())
+	entered := make(chan struct{})
+	release := make(chan struct{})
+	warmuper := NewWarmuper(ctx, WarmupConfig{
+		Enabled:    true,
+		CtxFactory: gatedCtxFactory(entered, release),
+		NumWorkers: 1,
+		MaxDepth:   64,
+		LogPrefix:  "test",
+	})
+	warmuper.Start()
+	defer warmuper.CloseAndWait()
+	defer close(release)
+
+	warmuper.WarmKey([]byte{0, 1, 2, 3}, 0, 0)
+	<-entered // worker is inside Branch holding the gen-0 item; slot 0 counter is 1
+	require.Equal(t, int64(1), warmuper.outstanding[0].Load())
+
+	errCh := make(chan error, 1)
+	go func() { errCh <- warmuper.WaitBufferFree(0) }()
+
+	select {
+	case <-errCh:
+		t.Fatal("WaitBufferFree returned before cancellation while the slot is in-flight")
+	case <-time.After(50 * time.Millisecond):
+	}
+
+	cancel()
+
+	select {
+	case err := <-errCh:
+		require.Error(t, err)
+	case <-time.After(2 * time.Second):
+		t.Fatal("WaitBufferFree did not return after the context was canceled")
+	}
+}
+
+// TestWarmuper_WaitBufferFree_FastPath verifies WaitBufferFree returns immediately when
+// the slot is already drained.
+func TestWarmuper_WaitBufferFree_FastPath(t *testing.T) {
+	t.Parallel()
+
+	warmuper := NewWarmuper(context.Background(), WarmupConfig{
+		Enabled:    true,
+		CtxFactory: noopCtxFactory,
+		NumWorkers: 1,
+		MaxDepth:   64,
+		LogPrefix:  "test",
+	})
+	warmuper.Start()
+	defer func() { require.NoError(t, warmuper.Wait()) }()
+
+	done := make(chan struct{})
+	go func() {
+		_ = warmuper.WaitBufferFree(0)
+		_ = warmuper.WaitBufferFree(1)
+		close(done)
+	}()
+	select {
+	case <-done:
+	case <-time.After(2 * time.Second):
+		t.Fatal("WaitBufferFree did not fast-path return on an already-drained slot")
+	}
+}
+
 func generateCellRow(tb testing.TB, size int) (row []*cell, bitmap uint16) {
 	tb.Helper()
 
```

### execution/commitment/warmuper.go
```diff
@@ -20,6 +20,7 @@ import (
 	"context"
 	"encoding/binary"
 	"fmt"
+	"sync"
 	"sync/atomic"
 	"time"
 
@@ -73,6 +74,12 @@ type Warmuper struct {
 	keysProcessed atomic.Uint64
 	startTime     time.Time
 
+	// Per-slot in-flight warm-item counts; the per-key path stays lock-free, mu/cond engage
+	// only on the drain-to-zero and WaitBufferFree paths.
+	outstanding [arenaRingSize]atomic.Int64
+	mu          sync.Mutex
+	cond        *sync.Cond
+
 	// State
 	started atomic.Bool
 	closed  atomic.Bool
@@ -81,6 +88,7 @@ type Warmuper struct {
 type warmupWorkItem struct {
 	hashedKey  []byte
 	startDepth int
+	gen        uint64
 }
 
 // NewWarmuper creates a new Warmuper instance.
@@ -97,6 +105,7 @@ func NewWarmuper(ctx context.Context, cfg WarmupConfig) *Warmuper {
 	if cfg.EnableWarmupCache {
 		w.cache = NewWarmupCache()
 	}
+	w.cond = sync.NewCond(&w.mu)
 	return w
 }
 
@@ -185,10 +194,20 @@ func (w *Warmuper) Start() {
 					}
 					w.warmupKey(trieCtx, item.hashedKey, item.startDepth)
 					w.keysProcessed.Add(1)
+					w.releaseGen(item.gen)
 				}
 			}
 		})
 	}
+
+	// Wake any WaitBufferFree waiter on shutdown so it observes cancellation instead of blocking on undrained items.
+	w.g.Go(func() error {
+		<-w.ctx.Done()
+		w.mu.Lock()
+		w.cond.Broadcast()
+		w.mu.Unlock()
+		return nil
+	})
 }
 
 // warmupKey performs the actual warmup for a single key by reading data to warm MDBX page cache.
@@ -269,19 +288,49 @@ func (w *Warmuper) warmupKey(trieCtx PatriciaContext, hashedKey []byte, startDep
 
 // WarmKey submits a hashed key for warming. Call Start() first.
 // startDepth indicates the depth from which to start warming (based on divergence from previous key).
-func (w *Warmuper) WarmKey(hashedKey []byte, startDepth int) {
+func (w *Warmuper) WarmKey(hashedKey []byte, startDepth int, gen uint64) {
 	if !w.started.Load() || w.numWorkers <= 0 || w.closed.Load() {
 		return
 	}
+	w.outstanding[gen%arenaRingSize].Add(1)
 	// Blocking By-Design!
 	// Speed of system is equal to speed of facing all page-faults during
 	// Or warmapers face them or main thread
 	// It means doesn't make much sense to unblock main thread if all Warmupers are loaded
 	// Anyway main thread can't run ahead of Warmupers (there are page-faults which will stop him)
 	select {
-	case w.work <- warmupWorkItem{hashedKey: hashedKey, startDepth: startDepth}:
+	case w.work <- warmupWorkItem{hashedKey: hashedKey, startDepth: startDepth, gen: gen}:
 	case <-w.ctx.Done():
+		w.releaseGen(gen)
+	}
+}
+
+// releaseGen decrements gen's ring-slot counter and wakes WaitBufferFree when the slot drains to zero.
+func (w *Warmuper) releaseGen(gen uint64) {
+	if w.outstanding[gen%arenaRingSize].Add(-1) == 0 {
+		w.mu.Lock()
+		w.cond.Broadcast()
+		w.mu.Unlock()
+	}
+}
+
+// WaitBufferFree blocks until every in-flight warm item for slot completes, or returns the context error if canceled first.
+func (w *Warmuper) WaitBufferFree(slot int) error {
+	if slot < 0 || slot >= arenaRingSize {
+		return fmt.Errorf("invalid arena slot %d", slot)
+	}
+	if w.outstanding[slot].Load() == 0 {
+		return nil
 	}
+	w.mu.Lock()
+	defer w.mu.Unlock()
+	for w.outstanding[slot].Load() != 0 {
+		if err := w.ctx.Err(); err != nil {
+			return err
+		}
+		w.cond.Wait()
+	}
+	return nil
 }
 
 // Wait waits for all warmup work to complete.
@@ -306,14 +355,15 @@ func (w *Warmuper) Stats() WarmupStats {
 	}
 }
 
-// DrainPending drains all pending work items from the work channel without processing them.
+// DrainPending discards queued work items, releasing each one's ring-slot counter so WaitBufferFree won't block on it.
 func (w *Warmuper) DrainPending() {
 	if !w.started.Load() || w.numWorkers <= 0 {
 		return
 	}
 	for {
 		select {
-		case <-w.work:
+		case item := <-w.work:
+			w.releaseGen(item.gen)
 		default:
 			return
 		}
```
