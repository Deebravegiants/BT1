# [?] fix posposen frames data race

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2019-06-17
Source: https://github.com/0xsoniclabs/sonic/commit/3dc3c1bab4014d7e8d376198dee95098ad4f6e8a
Type: security-commit

## Details
fix posposen frames data race

## Patch
### src/posposet/frames.go
```diff
@@ -5,6 +5,8 @@ import (
 	"sort"
 	"strings"
 
+	"github.com/pkg/errors"
+
 	"github.com/Fantom-foundation/go-lachesis/src/hash"
 )
 
@@ -63,6 +65,11 @@ func (p *Poset) FrameOfEvent(event hash.Event) (frame *Frame, isRoot bool) {
 	return
 }
 
+// frames errors
+var (
+	ErrIncorrectFrameKeyType = errors.New("incorrect type frames key")
+)
+
 // frame finds or creates frame.
 func (p *Poset) frame(n uint64, orCreate bool) *Frame {
 	if n < p.state.LastFinishedFrameN && orCreate {
@@ -75,61 +82,95 @@ func (p *Poset) frame(n uint64, orCreate bool) *Frame {
 			Balances: p.state.Genesis,
 		}
 	}
+
 	// return existing
-	f := p.frames[n]
-	if f == nil {
+	f, ok := p.frames.Load(n)
+	if !ok {
 		if !orCreate {
 			return nil
 		}
 		// create new frame
-		f = &Frame{
+		newFrame := &Frame{
 			Index:            n,
 			FlagTable:        FlagTable{},
 			ClothoCandidates: EventsByPeer{},
 			Atroposes:        TimestampsByEvent{},
 			Balances:         p.frame(n-1, true).Balances,
 		}
-		p.setFrameSaving(f)
-		p.frames[n] = f
-		f.save()
+		p.setFrameSaving(newFrame)
+		p.frames.Store(n, newFrame)
+		newFrame.save()
+		return newFrame
 	}
 
-	return f
+	return f.(*Frame)
+}
+
+func (p *Poset) framesNums() []uint64 {
+	var nums []uint64
+
+	p.frames.Range(func(key, value interface{}) bool {
+		n, ok := key.(uint64)
+		if !ok {
+			p.Fatal(ErrIncorrectFrameKeyType)
+		}
+
+		nums = append(nums, n)
+		return true
+	})
+
+	return nums
 }
 
 // frameNumsAsc returns frame numbers sorted from first to last.
 func (p *Poset) frameNumsAsc() []uint64 {
 	// TODO: cache sorted
-	var nums []uint64
-	for n := range p.frames {
-		nums = append(nums, n)
-	}
+	nums := p.framesNums()
 	sort.Sort(frameNums(nums))
 	return nums
 }
 
 // frameNumsDesc returns frame numbers sorted from last to first.
 func (p *Poset) frameNumsDesc() []uint64 {
 	// TODO: cache sorted
-	var nums []uint64
-	for n := range p.frames {
-		nums = append(nums, n)
-	}
+	nums := p.framesNums()
 	sort.Sort(sort.Reverse(frameNums(nums)))
 	return nums
 }
 
 // frameNumLast returns last frame number.
 func (p *Poset) frameNumLast() uint64 {
 	var max uint64
-	for n := range p.frames {
+	p.frames.Range(func(key, value interface{}) bool {
+		n, ok := key.(uint64)
+		if !ok {
+			p.Fatal(ErrIncorrectFrameKeyType)
+		}
+
 		if max < n {
 			max = n
 		}
-	}
+
+		return true
+	})
+
 	return max
 }
 
+func (p *Poset) mustFrameLoad(key uint64) *Frame {
+	f, ok := p.frames.Load(key)
+	if !ok {
+		p.Fatal(errors.Errorf("frame[%d] doesn't exist", key))
+	}
+
+	frame, ok := f.(*Frame)
+	if !ok {
+		p.Fatal(errors.New("incorrect type frame"))
+	}
+
+	return frame
+}
+
 /*
  * Utils:
  */
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
@@ -15,7 +16,7 @@ type Poset struct {
 	store  *Store
 	state  *State
 	input  EventSource
-	frames map[uint64]*Frame
+	frames *sync.Map
 
 	processingWg   sync.WaitGroup
 	processingDone chan struct{}
@@ -38,7 +39,7 @@ func New(store *Store, input EventSource) *Poset {
 	p := &Poset{
 		store:  store,
 		input:  input,
-		frames: make(map[uint64]*Frame),
+		frames: new(sync.Map),
 
 		newEventsCh: make(chan hash.Event, buffSize),
 
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
@@ -181,11 +182,18 @@ func (p *Poset) consensus(event *inter.Event) {
 	}
 
 	// clean old frames
-	for i := range p.frames {
+	p.frames.Range(func(key, value interface{}) bool {
+		i, ok := key.(uint64)
+		if !ok {
+			p.Fatal(ErrIncorrectFrameKeyType)
+		}
+
 		if i+stateGap < p.state.LastFinishedFrameN {
-			delete(p.frames, i)
+			p.frames.Delete(key)
 		}
-	}
+
+		return true
+	})
 }
 
 // checkIfRoot checks root-conditions for new event
@@ -230,10 +238,10 @@ func (p *Poset) checkIfRoot(e *Event) *Frame {
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
@@ -273,7 +281,7 @@ func (p *Poset) setClothoCandidates(root *Event, frame *Frame) {
 		// check CC-condition
 		if p.hasTrust(frame, roots) {
 			prev.AddClothoCandidate(seen, seenCreator)
-			//log.Debugf("CC: %s from %s", seen.String(), seenCreator.String())
+			// log.Debugf("CC: %s from %s", seen.String(), seenCreator.String())
 		}
 	}
 }
@@ -322,7 +330,7 @@ CLOTHO:
 					}
 
 					if diff%3 > 0 && p.hasMajority(prev, K) {
-						//log.Debugf("ATROPOS %s of frame %d", clotho.String(), frame.Index)
+						// log.Debugf("ATROPOS %s of frame %d", clotho.String(), frame.Index)
 						frame.SetAtropos(clotho, T)
 						has = true
 						continue CLOTHO
@@ -385,35 +393,35 @@ func (p *Poset) collectParents(a *Event, res *Events, already hash.Events) {
 }
 
 // reconsensusFromFrame recalcs consensus of frames.
-// It is not safe for concurrent use.
 func (p *Poset) reconsensusFromFrame(start uint64, newBalance hash.Hash) {
 	stop := p.frameNumLast()
 	var all inter.Events
 	// foreach stale frame
 	for n := start; n <= stop; n++ {
-		frame := p.frames[n]
+		frame := p.mustFrameLoad(n)
 		// extract events
 		for e := range frame.FlagTable {
 			if !frame.FlagTable.IsRoot(e) {
 				all = append(all, p.GetEvent(e).Event)
 			}
 		}
 		// and replace stale frame with blank
-		p.frames[n] = &Frame{
+		p.frames.Store(n, &Frame{
 			Index:            n,
 			FlagTable:        FlagTable{},
 			ClothoCandidates: EventsByPeer{},
 			Atroposes:        TimestampsByEvent{},
 			Balances:         newBalance,
-		}
+		})
 	}
 	// recalc consensus (without frame saving)
 	for _, e := range all.ByParents() {
 		p.consensus(e)
 	}
 	// save fresh frame
 	for n := start; n <= stop; n++ {
-		frame := p.frames[n]
+		frame := p.mustFrameLoad(n)
+
 		p.setFrameSaving(frame)
 		frame.Save()
 	}
```

### src/posposet/state.go
```diff
@@ -61,7 +61,7 @@ func (p *Poset) Bootstrap() {
 	// restore frames
 	for n := p.state.LastFinishedFrameN; true; n++ {
 		if f := p.store.GetFrame(n); f != nil {
-			p.frames[n] = f
+			p.frames.Store(n, f)
 		} else if n > 0 {
 			break
 		}
```
