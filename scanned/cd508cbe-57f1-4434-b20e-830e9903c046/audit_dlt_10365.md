# [?] overflow checks, time offset fix

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2019-09-20
Source: https://github.com/0xsoniclabs/sonic/commit/f7a05679b3b7799dd1cdd1a9a2b551e04714650d
Type: security-commit

## Details
overflow checks, time offset fix

Merge pull request #329 from devintegral2/feature/upper_limit

## Patch
### src/event_check/basic_check/basic_check.go
```diff
@@ -2,6 +2,7 @@ package basic_check
 
 import (
 	"errors"
+	"math"
 
 	"github.com/ethereum/go-ethereum/core/types"
 	"github.com/ethereum/go-ethereum/params"
@@ -37,6 +38,7 @@ var (
 	ErrNotInited      = errors.New("event field is not initialized")
 	ErrZeroTime       = errors.New("event has zero timestamp")
 	ErrNegativeValue  = errors.New("negative value")
+	ErrHugeValue      = errors.New("too big value")
 )
 
 // Check which don't require anything except event
@@ -118,6 +120,10 @@ func (v *Validator) checkInited(e *inter.Event) error {
 	if e.Seq <= 0 || e.Epoch <= 0 || e.Frame <= 0 || e.Lamport <= 0 {
 		return ErrNotInited // it's unsigned, but check for negative in a case if type will change
 	}
+	if e.Seq >= math.MaxInt32/2 || e.Epoch >= math.MaxInt32/2 || e.Frame >= math.MaxInt32/2 || e.Lamport >= math.MaxInt32/2 {
+		return ErrHugeValue
+	}
+
 	if e.ClaimedTime <= 0 {
 		return ErrZeroTime
 	}
```

### src/gossip/packs_downloader/peer_downloader.go
```diff
@@ -2,6 +2,7 @@ package packs_downloader
 
 import (
 	"errors"
+	"math"
 	"time"
 
 	tree "github.com/emirpasic/gods/maps/treemap"
@@ -218,7 +219,7 @@ func (d *PeerPacksDownloader) loop() {
 				log.Error("All the peer packs are unknown. Faulty peer?", "peer", d.peer.Id)
 				d.dropPeer(d.peer.Id)
 			}
-			if packInfo.index == 0 {
+			if packInfo.index <= 0 || packInfo.index >= math.MaxInt32 {
 				log.Error("invalid pack index", "peer", d.peer.Id)
 				continue
 			}
```

### src/poset/apply_genesis.go
```diff
@@ -34,8 +34,8 @@ func (g *GenesisState) EpochName() string {
 	return fmt.Sprintf("epoch%d", g.Epoch)
 }
 
-// calcFirstGenesisHash calcs hash of genesis balances.
-func calcFirstGenesisHash(g *genesis.Genesis, genesisAtropos hash.Event, stateHash common.Hash) common.Hash {
+// calcGenesisHash calcs hash of genesis balances.
+func calcGenesisHash(g *genesis.Genesis, genesisAtropos hash.Event, stateHash common.Hash) common.Hash {
 	s := NewMemStore()
 	defer s.Close()
 
@@ -54,7 +54,7 @@ func (s *Store) ApplyGenesis(g *genesis.Genesis, genesisAtropos hash.Event, stat
 	}
 
 	if exist := s.GetGenesis(); exist != nil {
-		if exist.PrevEpoch.Hash() == calcFirstGenesisHash(g, genesisAtropos, stateHash) {
+		if exist.PrevEpoch.Hash() == calcGenesisHash(g, genesisAtropos, stateHash) {
 			return nil
 		}
 		return fmt.Errorf("other genesis has applied already")
```

### src/poset/epoch.go
```diff
@@ -45,14 +45,11 @@ func (p *Poset) GetEpochMembers() (pos.Members, idx.Epoch) {
 // rootForklessCausesRoot returns hash of root B, if root A forkless causes root B.
 // Due to a fork, there may be many roots B with the same slot,
 // but forkless caused may be only one of them (if no more than 1/3n are Byzantine), with a specific hash.
-func (p *Poset) rootForklessCausesRoot(a hash.Event, bNode common.Address, bFrame idx.Frame) *hash.Event {
+func (p *Poset) rootForklessCausesRoot(a hash.Event, bCreator common.Address, bFrame idx.Frame) *hash.Event {
 	var bHash *hash.Event
-	p.store.ForEachRootFrom(bFrame, bNode, func(f idx.Frame, from common.Address, b hash.Event) bool {
-		if f != bFrame {
-			p.Log.Crit("frame mismatch")
-		}
-		if from != bNode {
-			p.Log.Crit("node mismatch")
+	p.store.ForEachRootFrom(bFrame, bCreator, func(f idx.Frame, from common.Address, b hash.Event) bool {
+		if f != bFrame || from != bCreator {
+			p.Log.Crit("inconsistent DB iteration")
 		}
 		if p.vecClock.ForklessCause(a, b) {
 			bHash = &b
```

### src/poset/event_ordering.go
```diff
@@ -38,10 +38,10 @@ func (p *Poset) fareOrdering(frame idx.Frame, atropos hash.Event, unordered []*i
 	timeRatio := inter.MaxTimestamp(frameTimePeriod/inter.Timestamp(frameLamportPeriod), 1)
 
 	lowestConsensusTime := p.LastConsensusTime + timeRatio
-	timeOffset := lowestConsensusTime - inter.Timestamp(lowestLamport)*timeRatio
+	timeOffset := int64(lowestConsensusTime) - int64(lowestLamport)*int64(timeRatio)
 
 	// Calculate consensus timestamp of an event with highestLamport (it's always atropos)
-	p.LastConsensusTime = inter.Timestamp(highestLamport)*timeRatio + timeOffset
+	p.LastConsensusTime = inter.Timestamp(int64(highestLamport)*int64(timeRatio) + timeOffset)
 
 	// Save new timeRatio & timeOffset to frame
 	p.store.SetFrameInfo(p.EpochN, frame, &FrameInfo{
```

### src/poset/frame_info.go
```diff
@@ -2,16 +2,41 @@ package poset
 
 import (
 	"github.com/Fantom-foundation/go-lachesis/src/inter"
+	"github.com/ethereum/go-ethereum/rlp"
+	"io"
+	"math"
 )
 
 // TODO: make FrameInfo internal
 
 type FrameInfo struct {
-	TimeOffset inter.Timestamp
+	TimeOffset int64 // may be negative
 	TimeRatio  inter.Timestamp
 }
 
+type frameInfoMarshaling struct {
+	TimeOffset uint64
+	TimeRatio  inter.Timestamp
+}
+
+func (f *FrameInfo) EncodeRLP(w io.Writer) error {
+	return rlp.Encode(w, frameInfoMarshaling{
+		TimeOffset: uint64(f.TimeOffset + math.MaxInt64/2),
+		TimeRatio:  f.TimeRatio,
+	})
+}
+
+func (f *FrameInfo) DecodeRLP(st *rlp.Stream) error {
+	m := frameInfoMarshaling{}
+	if err := st.Decode(&m); err != nil {
+		return err
+	}
+	f.TimeOffset = int64(m.TimeOffset) - math.MaxInt64/2
+	f.TimeRatio = m.TimeRatio
+	return nil
+}
+
 // GetConsensusTimestamp calc consensus timestamp for given event.
 func (f *FrameInfo) GetConsensusTimestamp(e *Event) inter.Timestamp {
-	return inter.Timestamp(e.Lamport)*f.TimeOffset + f.TimeRatio
+	return inter.Timestamp(int64(e.Lamport)*int64(f.TimeRatio) + f.TimeOffset)
 }
```

### src/poset/frame_info_test.go
```diff
@@ -3,15 +3,33 @@ package poset
 import (
 	"github.com/ethereum/go-ethereum/rlp"
 	"github.com/stretchr/testify/assert"
+	"math"
 	"testing"
 )
 
 func TestFrameInfoSerialization(t *testing.T) {
 	assertar := assert.New(t)
 
 	f0 := &FrameInfo{
-		TimeOffset: 3,
-		TimeRatio:  1,
+		TimeOffset: math.MaxInt64 / 2,
+		TimeRatio:  math.MaxUint64,
+	}
+	buf, err := rlp.EncodeToBytes(f0)
+	assertar.NoError(err)
+
+	f1 := &FrameInfo{}
+	err = rlp.DecodeBytes(buf, f1)
+	assertar.NoError(err)
+
+	assertar.EqualValues(f0, f1)
+}
+
+func TestFrameInfoSerializationSigned(t *testing.T) {
+	assertar := assert.New(t)
+
+	f0 := &FrameInfo{
+		TimeOffset: -math.MaxInt64 / 2,
+		TimeRatio:  0,
 	}
 	buf, err := rlp.EncodeToBytes(f0)
 	assertar.NoError(err)
```

### src/poset/poset.go
```diff
@@ -196,7 +196,7 @@ func (p *Poset) ProcessEvent(e *inter.Event) error {
 }
 
 // calcFrameIdx checks root-conditions for new event
-// and returns frame where event is root.
+// and returns event's frame.
 // It is not safe for concurrent use.
 func (p *Poset) calcFrameIdx(e *inter.Event, checkOnly bool) (frame idx.Frame, isRoot bool) {
 	if e.SelfParent() == nil {
```

### src/poset/poset_test.go
```diff
@@ -61,11 +61,11 @@ func TestPoset(t *testing.T) {
 			p0 := posets[i]
 			st0 := p0.store.GetCheckpoint()
 			ep0 := p0.store.GetEpoch()
-			t.Logf("Compare poset%d: SFrame %d, Block %d", i, ep0.EpochN, st0.LastBlockN)
+			t.Logf("Compare poset%d: Epoch %d, Block %d", i, ep0.EpochN, st0.LastBlockN)
 			for j := i + 1; j < len(posets); j++ {
 				p1 := posets[j]
 				st1 := p1.store.GetCheckpoint()
-				t.Logf("with poset%d: SFrame %d, Block %d", j, ep0.EpochN, st1.LastBlockN)
+				t.Logf("with poset%d: Epoch %d, Block %d", j, ep0.EpochN, st1.LastBlockN)
 
 				assertar.Equal(*posets[j].checkpoint, *posets[i].checkpoint)
 				assertar.Equal(posets[j].epochState, posets[i].epochState)
```

### src/poset/time.go
```diff
@@ -1,68 +0,0 @@
-package poset
-
-import (
-	"math"
-
-	"github.com/Fantom-foundation/go-lachesis/src/hash"
-	"github.com/Fantom-foundation/go-lachesis/src/inter"
-)
-
-type (
-	// TimestampsByEvent is a timestamps by event index.
-	TimestampsByEvent map[hash.Event]inter.Timestamp
-)
-
-// ToWire converts to simple slice.
-func (tt TimestampsByEvent) ToWire() map[string]uint64 {
-	res := make(map[string]uint64, len(tt))
-
-	for e, t := range tt {
-		res[e.Hex()] = uint64(t)
-	}
-
-	return res
-}
-
-// WireToTimestampsByEvent converts from wire.
-func WireToTimestampsByEvent(arr map[string]uint64) TimestampsByEvent {
-	res := make(TimestampsByEvent, len(arr))
-
-	for hex, t := range arr {
-		hash_ := hash.HexToEventHash(hex)
-		res[hash_] = inter.Timestamp(t)
-	}
-
-	return res
-}
-
-/*
- * timeCounter:
- */
-
-type timeCounter map[inter.Timestamp]uint
-
-func (c timeCounter) Add(t inter.Timestamp) {
-	c[t]++
-}
-
-func (c timeCounter) MaxMin() inter.Timestamp {
-	var maxs []inter.Timestamp
-	freq := uint(0)
-	for t, n := range c {
-		if n > freq {
-			maxs = []inter.Timestamp{t}
-			freq = n
-		}
-		if n == freq {
-			maxs = append(maxs, t)
-		}
-	}
-
-	min := inter.Timestamp(math.MaxUint64)
-	for _, t := range maxs {
-		if min > t {
-			min = t
-		}
-	}
-	return min
-}
```

### src/poset/time_test.go
```diff
@@ -1,33 +0,0 @@
-package poset
-
-import (
-	"math"
-	"testing"
-
-	"github.com/stretchr/testify/assert"
-
-	"github.com/Fantom-foundation/go-lachesis/src/inter"
-)
-
-func TestLamportTimeCounter(t *testing.T) {
-	assertar := assert.New(t)
-
-	data := map[inter.Timestamp][]inter.Timestamp{
-		math.MaxUint64: {},
-		3:              {3},
-		10:             {9, 10, 10, 11},
-		2:              {10, 9, 10, 10, 11, 2, 8, 2, 2, 1, 1},
-	}
-
-	for expected, vals := range data {
-		counter := timeCounter{}
-		for _, t := range vals {
-			counter.Add(t)
-		}
-
-		actual := counter.MaxMin()
-		if !assertar.Equal(expected, actual, "max-min time") {
-			break
-		}
-	}
-}
```

### src/poset/transaction_test.go
```diff
@@ -83,5 +83,5 @@ func TestPosetTxn(t *testing.T) {
 
 	st := s.GetCheckpoint()
 	ep := s.GetEpoch()
-	t.Logf("poset: SFrame %d, Block %d", ep.EpochN, st.LastBlockN)
+	t.Logf("poset: Epoch %d, Block %d", ep.EpochN, st.LastBlockN)
 }
```
