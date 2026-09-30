# [?] Fix race condition

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2026-01-07
Source: https://github.com/kaiachain/kaia/commit/c630086b0af4f9e722b88fed7588e2294028f2f0
Type: security-commit

## Details
Fix race condition

## Patch
### consensus/istanbul/core/core.go
```diff
@@ -307,14 +307,6 @@ func (c *core) startNewRound(round *big.Int) {
 
 	logger.Debug("New round", "new_round", newView.Round, "new_seq", newView.Sequence, "new_proposer", c.currentCommittee.Proposer(), "isProposer", c.isProposer())
 	logger.Trace("New round", "new_round", newView.Round, "new_seq", newView.Sequence, "size", c.currentCommittee.Qualified().Len(), "valSet", c.currentCommittee.Qualified().String())
-
-	if Vrank == nil {
-		Vrank = NewVrank(*c.currentView(), c.currentCommittee.Committee().List(), c.currentCommittee.RequiredMessageCount())
-	} else {
-		// log the previous round's vrank
-		Vrank.Log()
-		Vrank.StartNewRound(*c.currentView(), c.currentCommittee.Committee().List(), c.currentCommittee.RequiredMessageCount())
-	}
 }
 
 func (c *core) catchUpRound(view *istanbul.View) {
```

### consensus/istanbul/core/prepare.go
```diff
@@ -77,6 +77,11 @@ func (c *core) handlePrepare(msg *message, src common.Address) error {
 
 	c.acceptPrepare(msg, src)
 
+	// in case of proposer, view is not set from handlePreprepare(), thus set here
+	if Vrank != nil {
+		Vrank.SetLatestView(*prepare.View, c.currentCommittee.Committee().List(), c.currentCommittee.RequiredMessageCount())
+	}
+
 	// Change to Prepared state if we've received enough PREPARE/COMMIT messages or it is locked
 	// and we are in earlier state before Prepared state.
 	// Both of PREPARE and COMMIT messages are counted since the nodes which is hashlocked in
```

### consensus/istanbul/core/preprepare.go
```diff
@@ -69,6 +69,7 @@ func (c *core) handlePreprepare(msg *message, src common.Address) error {
 	}
 
 	if Vrank != nil {
+		Vrank.SetLatestView(*preprepare.View, c.currentCommittee.Committee().List(), c.currentCommittee.RequiredMessageCount())
 		Vrank.AddPreprepare(preprepare, src)
 	}
 
```

### consensus/istanbul/core/vrank.go
```diff
@@ -21,7 +21,6 @@ package core
 import (
 	"fmt"
 	"maps"
-	"math/big"
 	"slices"
 	"time"
 
@@ -53,44 +52,23 @@ var (
 	Vrank *vrank
 )
 
-const (
-	vrankArrivedEarly = iota
-	vrankArrivedLate
-	vrankNotArrived
-)
-
-const (
-	vrankNotArrivedPlaceholder = -1
-)
-
-func NewVrank(view istanbul.View, committee []common.Address, quorum int) *vrank {
-	if quorum == 0 {
-		return nil
-	}
-
-	return &vrank{
-		view:                  view,
-		committee:             committee,
-		quorum:                quorum,
-		commitArrivalTimeMap:  make(map[common.Address]time.Duration),
-		preprepareArrivalTime: time.Duration(0),
-	}
+func NewVrank() *vrank {
+	return &vrank{}
 }
 
 func (v *vrank) StartTimer() {
 	v.miningStartTime = time.Now()
+	v.preprepareArrivalTime = time.Duration(0)
+	v.commitArrivalTimeMap = make(map[common.Address]time.Duration)
+	v.view = istanbul.View{}
+	v.committee = []common.Address{}
+	v.quorum = 0
 }
 
-func (v *vrank) StartNewRound(view istanbul.View, committee []common.Address, quorum int) {
-	// preserve miningStartTime for the first round
-	if view.Round.Cmp(big.NewInt(0)) == 0 {
-		v.miningStartTime = time.Time{}
-	}
+func (v *vrank) SetLatestView(view istanbul.View, committee []common.Address, quorum int) {
 	v.view = view
 	v.committee = committee
 	v.quorum = quorum
-	v.commitArrivalTimeMap = make(map[common.Address]time.Duration)
-	v.preprepareArrivalTime = time.Duration(0)
 }
 
 func (v *vrank) AddPreprepare(msg *istanbul.Preprepare, src common.Address) {
@@ -105,8 +83,42 @@ func (v *vrank) AddCommit(msg *istanbul.Subject, src common.Address) {
 	}
 }
 
+func (v *vrank) isTargetPreprepare(msg *istanbul.Preprepare, src common.Address) bool {
+	if msg.View == nil || msg.View.Sequence == nil || msg.View.Round == nil {
+		return false
+	}
+	if v.view.Sequence == nil || v.view.Round == nil {
+		return false
+	}
+	if msg.View.Cmp(&v.view) != 0 {
+		return false
+	}
+	return true
+}
+
+func (v *vrank) isTargetCommit(msg *istanbul.Subject, src common.Address) bool {
+	if msg.View == nil || msg.View.Sequence == nil || msg.View.Round == nil {
+		return false
+	}
+	if v.view.Sequence == nil || v.view.Round == nil {
+		return false
+	}
+	if msg.View.Cmp(&v.view) != 0 {
+		return false
+	}
+	if _, ok := v.commitArrivalTimeMap[src]; ok {
+		return false
+	}
+	return true
+}
+
 // Log logs accumulated data in a compressed form
 func (v *vrank) Log() {
+	// Skip if no data collected (view not set)
+	if v.view.Sequence == nil || v.view.Round == nil {
+		return
+	}
+
 	v.updateMetrics()
 
 	// Skip logging if VRankLogFrequency is 0 or not in the logging frequency
@@ -173,30 +185,6 @@ func (v *vrank) updateMetrics() {
 	}
 }
 
-func (v *vrank) isTargetPreprepare(msg *istanbul.Preprepare, src common.Address) bool {
-	if msg.View == nil || msg.View.Sequence == nil || msg.View.Round == nil {
-		return false
-	}
-	if msg.View.Cmp(&v.view) != 0 {
-		return false
-	}
-	return true
-}
-
-func (v *vrank) isTargetCommit(msg *istanbul.Subject, src common.Address) bool {
-	if msg.View == nil || msg.View.Sequence == nil || msg.View.Round == nil {
-		return false
-	}
-	if msg.View.Cmp(&v.view) != 0 {
-		return false
-	}
-	_, ok := v.commitArrivalTimeMap[src]
-	if ok {
-		return false
-	}
-	return true
-}
-
 // encodeDuration encodes given duration into string
 func encodeDuration(d time.Duration) string {
 	return fmt.Sprintf("%d", d.Milliseconds())
```

### consensus/istanbul/core/vrank_test.go
```diff
@@ -40,6 +40,7 @@ func TestVrank(t *testing.T) {
 	)
 
 	vrank.StartTimer()
+	vrank.SetLatestView(view, committee, quorum)
 	time.Sleep(1 * time.Millisecond)
 
 	for i := 0; i < quorum; i++ {
```

### work/worker.go
```diff
@@ -562,8 +562,11 @@ func (self *worker) commitNewWork() {
 		}
 
 		if core.Vrank != nil {
-			core.Vrank.StartTimer()
+			core.Vrank.Log()
+		} else {
+			core.Vrank = core.NewVrank()
 		}
+		core.Vrank.StartTimer()
 	}
 
 	var pending map[common.Address]types.Transactions
```
