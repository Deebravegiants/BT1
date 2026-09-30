# [?] posposet data race fix

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2019-06-23
Source: https://github.com/0xsoniclabs/sonic/commit/985f50acf40c36d9957584d8d0bb0b6dfb1ed984
Type: security-commit

## Details
posposet data race fix

Merge pull request #236 from devintegral4/posposet_frames_data_race

## Patch
### src/poslachesis/lachesis_test.go
```diff
@@ -21,7 +21,7 @@ func TestRing(t *testing.T) {
 
 	for _, l := range ll {
 		st := l.consensusStore.GetState()
-		t.Logf("%s: frame %d, block %d", l.node.Host(), st.LastFinishedFrameN, st.LastBlockN)
+		t.Logf("%s: frame %d, block %d", l.node.Host(), st.LastFinishedFrameN(), st.LastBlockN)
 		l.Stop()
 	}
 }
@@ -35,7 +35,7 @@ func TestStar(t *testing.T) {
 
 	for _, l := range ll {
 		st := l.consensusStore.GetState()
-		t.Logf("%s: frame %d, block %d", l.node.Host(), st.LastFinishedFrameN, st.LastBlockN)
+		t.Logf("%s: frame %d, block %d", l.node.Host(), st.LastFinishedFrameN(), st.LastBlockN)
 		l.Stop()
 	}
 }
```

### src/posposet/frame.go
```diff
@@ -98,7 +98,7 @@ func WireToFrame(w *wire.Frame) *Frame {
 
 func (p *Poset) setFrameSaving(f *Frame) {
 	f.save = func() {
-		if f.Index > p.state.LastFinishedFrameN {
+		if f.Index > p.state.LastFinishedFrameN() {
 			p.store.SetFrame(f)
 		} else {
 			p.Fatalf("frame %d is finished and should not be changed", f.Index)
```

### src/posposet/frames.go
```diff
@@ -63,9 +63,29 @@ func (p *Poset) FrameOfEvent(event hash.Event) (frame *Frame, isRoot bool) {
 	return
 }
 
+func (p *Poset) frameFromStore(n uint64) *Frame {
+	if n < p.state.LastFinishedFrameN() {
+		p.Fatalf("too old frame %d is requested", n)
+	}
+	// return ephemeral
+	if n == 0 {
+		return &Frame{
+			Index:    0,
+			Balances: p.state.Genesis,
+		}
+	}
+
+	f := p.store.GetFrame(n)
+	if f == nil {
+		return p.frameFromStore(n - 1)
+	}
+
+	return f
+}
+
 // frame finds or creates frame.
 func (p *Poset) frame(n uint64, orCreate bool) *Frame {
-	if n < p.state.LastFinishedFrameN && orCreate {
+	if n < p.state.LastFinishedFrameN() && orCreate {
 		p.Fatalf("too old frame %d is requested", n)
 	}
 	// return ephemeral
@@ -75,9 +95,10 @@ func (p *Poset) frame(n uint64, orCreate bool) *Frame {
 			Balances: p.state.Genesis,
 		}
 	}
+
 	// return existing
-	f := p.frames[n]
-	if f == nil {
+	f, ok := p.frames[n]
+	if !ok {
 		if !orCreate {
 			return nil
 		}
@@ -97,35 +118,14 @@ func (p *Poset) frame(n uint64, orCreate bool) *Frame {
 	return f
 }
 
-// frameNumsAsc returns frame numbers sorted from first to last.
-func (p *Poset) frameNumsAsc() []uint64 {
-	// TODO: cache sorted
-	var nums []uint64
-	for n := range p.frames {
-		nums = append(nums, n)
-	}
-	sort.Sort(frameNums(nums))
-	return nums
-}
-
-// frameNumsDesc returns frame numbers sorted from last to first.
-func (p *Poset) frameNumsDesc() []uint64 {
-	// TODO: cache sorted
-	var nums []uint64
-	for n := range p.frames {
-		nums = append(nums, n)
-	}
-	sort.Sort(sort.Reverse(frameNums(nums)))
-	return nums
-}
-
 // frameNumLast returns last frame number.
 func (p *Poset) frameNumLast() uint64 {
 	var max uint64
 	for n := range p.frames {
 		if max < n {
 			max = n
 		}
+
 	}
 	return max
 }
```

### src/posposet/poset.go
```diff
@@ -1,10 +1,11 @@
 package posposet
 
 import (
-	"errors"
 	"sort"
 	"sync"
 
+	"github.com/pkg/errors"
+
 	"github.com/Fantom-foundation/go-lachesis/src/hash"
 	"github.com/Fantom-foundation/go-lachesis/src/inter"
 	"github.com/Fantom-foundation/go-lachesis/src/logger"
@@ -70,11 +71,11 @@ func (p *Poset) Start() {
 	p.processingWg.Add(1)
 	go func() {
 		defer p.processingWg.Done()
-		//log.Debug("Start of events processing ...")
+		// log.Debug("Start of events processing ...")
 		for {
 			select {
 			case <-p.processingDone:
-				//log.Debug("Stop of events processing ...")
+				// log.Debug("Stop of events processing ...")
 				return
 			case e := <-p.newEventsCh:
 				event := p.input.GetEvent(e)
@@ -138,8 +139,8 @@ func (p *Poset) consensus(event *inter.Event) {
 
 	// process matured frames where ClothoCandidates have become Clothos
 	var ordered inter.Events
-	lastFinished := p.state.LastFinishedFrameN
-	for n := p.state.LastFinishedFrameN + 1; n+3 <= frame.Index; n++ {
+	lastFinished := p.state.LastFinishedFrameN()
+	for n := p.state.LastFinishedFrameN() + 1; n+3 <= frame.Index; n++ {
 		if p.hasAtropos(n, frame.Index) {
 			p.Debugf("consensus: make new block %d from frame %d", p.state.LastBlockN+1, n)
 			events := p.topologicalOrdered(n)
@@ -174,15 +175,15 @@ func (p *Poset) consensus(event *inter.Event) {
 	}
 
 	// save finished frames
-	if p.state.LastFinishedFrameN < lastFinished {
-		p.state.LastFinishedFrameN = lastFinished
+	if p.state.LastFinishedFrameN() < lastFinished {
+		p.state.LastFinishedFrame(lastFinished)
 		p.saveState()
-		p.Debugf("consensus: lastFinishedFrameN is %d", p.state.LastFinishedFrameN)
+		p.Debugf("consensus: lastFinishedFrameN is %d", p.state.LastFinishedFrameN())
 	}
 
 	// clean old frames
 	for i := range p.frames {
-		if i+stateGap < p.state.LastFinishedFrameN {
+		if i+stateGap < p.state.LastFinishedFrameN() {
 			delete(p.frames, i)
 		}
 	}
@@ -193,11 +194,11 @@ func (p *Poset) consensus(event *inter.Event) {
 // It is not safe for concurrent use.
 func (p *Poset) checkIfRoot(e *Event) *Frame {
 	knownRoots := eventsByFrame{}
-	minFrame := p.state.LastFinishedFrameN + 1
+	minFrame := p.state.LastFinishedFrameN() + 1
 	for parent := range e.Parents {
 		if !parent.IsZero() {
 			frame, isRoot := p.FrameOfEvent(parent)
-			if frame == nil || frame.Index <= p.state.LastFinishedFrameN {
+			if frame == nil || frame.Index <= p.state.LastFinishedFrameN() {
 				p.Warnf("Parent %s of %s is too old. Skipped", parent.String(), e.String())
 				// NOTE: is it possible some participants got this event before parent outdated?
 				continue
@@ -230,10 +231,10 @@ func (p *Poset) checkIfRoot(e *Event) *Frame {
 		roots := knownRoots[fnum]
 		frame = p.frame(fnum, true)
 		frame.AddRootsOf(e.Hash(), roots)
-		//log.Debugf(" %s knows %s at frame %d", e.Hash().String(), roots.String(), frame.Index)
+		// log.Debugf(" %s knows %s at frame %d", e.Hash().String(), roots.String(), frame.Index)
 		if isRoot = p.hasMajority(frame, roots); isRoot {
 			frame = p.frame(fnum+1, true)
-			//log.Debugf(" %s is root of frame %d", e.Hash().String(), frame.Index)
+			// log.Debugf(" %s is root of frame %d", e.Hash().String(), frame.Index)
 			break
 		}
 	}
@@ -273,7 +274,7 @@ func (p *Poset) setClothoCandidates(root *Event, frame *Frame) {
 		// check CC-condition
 		if p.hasTrust(frame, roots) {
 			prev.AddClothoCandidate(seen, seenCreator)
-			//log.Debugf("CC: %s from %s", seen.String(), seenCreator.String())
+			// log.Debugf("CC: %s from %s", seen.String(), seenCreator.String())
 		}
 	}
 }
@@ -322,7 +323,7 @@ CLOTHO:
 					}
 
 					if diff%3 > 0 && p.hasMajority(prev, K) {
-						//log.Debugf("ATROPOS %s of frame %d", clotho.String(), frame.Index)
+						// log.Debugf("ATROPOS %s of frame %d", clotho.String(), frame.Index)
 						frame.SetAtropos(clotho, T)
 						has = true
 						continue CLOTHO
@@ -385,7 +386,6 @@ func (p *Poset) collectParents(a *Event, res *Events, already hash.Events) {
 }
 
 // reconsensusFromFrame recalcs consensus of frames.
-// It is not safe for concurrent use.
 func (p *Poset) reconsensusFromFrame(start uint64, newBalance hash.Hash) {
 	stop := p.frameNumLast()
 	var all inter.Events
@@ -414,6 +414,7 @@ func (p *Poset) reconsensusFromFrame(start uint64, newBalance hash.Hash) {
 	// save fresh frame
 	for n := start; n <= stop; n++ {
 		frame := p.frames[n]
+
 		p.setFrameSaving(frame)
 		frame.Save()
 	}
```

### src/posposet/poset_test.go
```diff
@@ -69,7 +69,7 @@ func TestPoset(t *testing.T) {
 		for i := 0; i < len(posets)-1; i++ {
 			p0 := posets[i]
 			st := p0.store.GetState()
-			t.Logf("poset%d: frame %d, block %d", i, st.LastFinishedFrameN, st.LastBlockN)
+			t.Logf("poset%d: frame %d, block %d", i, st.LastFinishedFrameN(), st.LastBlockN)
 			for j := i + 1; j < len(posets); j++ {
 				p1 := posets[j]
 
```

### src/posposet/stake.go
```diff
@@ -33,7 +33,7 @@ func (s *stakeCounter) IsGoalAchieved() bool {
 
 // StakeOf returns last stake balance of peer.
 func (p *Poset) StakeOf(addr hash.Peer) uint64 {
-	f := p.frame(p.state.LastFinishedFrameN+stateGap, true)
+	f := p.frameFromStore(p.state.LastFinishedFrameN() + stateGap)
 	db := p.store.StateDB(f.Balances)
 	return db.VoteBalance(addr)
 }
```

### src/posposet/state.go
```diff
@@ -1,6 +1,8 @@
 package posposet
 
 import (
+	"sync/atomic"
+
 	"github.com/Fantom-foundation/go-lachesis/src/hash"
 	"github.com/Fantom-foundation/go-lachesis/src/logger"
 	"github.com/Fantom-foundation/go-lachesis/src/posposet/wire"
@@ -10,16 +12,24 @@ import (
 
 // State is a current poset state.
 type State struct {
-	LastFinishedFrameN uint64
+	lastFinishedFrameN uint64
 	LastBlockN         uint64
 	Genesis            hash.Hash
 	TotalCap           uint64
 }
 
+func (s *State) LastFinishedFrameN() uint64 {
+	return atomic.LoadUint64(&s.lastFinishedFrameN)
+}
+
+func (s *State) LastFinishedFrame(N uint64) {
+	atomic.StoreUint64(&s.lastFinishedFrameN, N)
+}
+
 // ToWire converts to proto.Message.
 func (s *State) ToWire() *wire.State {
 	return &wire.State{
-		LastFinishedFrameN: s.LastFinishedFrameN,
+		LastFinishedFrameN: s.LastFinishedFrameN(),
 		LastBlockN:         s.LastBlockN,
 		Genesis:            s.Genesis.Bytes(),
 		TotalCap:           s.TotalCap,
@@ -32,7 +42,7 @@ func WireToState(w *wire.State) *State {
 		return nil
 	}
 	return &State{
-		LastFinishedFrameN: w.LastFinishedFrameN,
+		lastFinishedFrameN: w.LastFinishedFrameN,
 		LastBlockN:         w.LastBlockN,
 		Genesis:            hash.FromBytes(w.Genesis),
 		TotalCap:           w.TotalCap,
@@ -59,16 +69,16 @@ func (p *Poset) Bootstrap() {
 		p.Fatal("Apply genesis for store first")
 	}
 	// restore frames
-	for n := p.state.LastFinishedFrameN; true; n++ {
+	for n := p.state.LastFinishedFrameN(); true; n++ {
 		if f := p.store.GetFrame(n); f != nil {
 			p.frames[n] = f
 		} else if n > 0 {
 			break
 		}
 	}
 	// recalc in case there was a interrupted consensus
-	start := p.frame(p.state.LastFinishedFrameN, true)
-	p.reconsensusFromFrame(p.state.LastFinishedFrameN+1, start.Balances)
+	start := p.frame(p.state.LastFinishedFrameN(), true)
+	p.reconsensusFromFrame(p.state.LastFinishedFrameN()+1, start.Balances)
 }
 
 func (p *Poset) GetGenesisHash() hash.Hash {
```

### src/posposet/store.go
```diff
@@ -86,7 +86,7 @@ func (s *Store) ApplyGenesis(balances map[hash.Peer]uint64) error {
 	}
 
 	st = &State{
-		LastFinishedFrameN: 0,
+		lastFinishedFrameN: 0,
 		TotalCap:           0,
 	}
 
```

### src/posposet/transaction_test.go
```diff
@@ -47,7 +47,7 @@ func TestPosetTxn(t *testing.T) {
 	}
 
 	st := s.GetState()
-	t.Logf("poset: frame %d, block %d", st.LastFinishedFrameN, st.LastBlockN)
+	t.Logf("poset: frame %d, block %d", st.LastFinishedFrameN(), st.LastBlockN)
 
 	assert.Equal(t,
 		uint64(0), p.StakeOf(nodes[0]),
```
