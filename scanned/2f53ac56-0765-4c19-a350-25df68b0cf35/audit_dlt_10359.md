# [?] fix frames deadlock with cheaters

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2019-12-24
Source: https://github.com/0xsoniclabs/sonic/commit/444f0f7c219e14e6426bc1f38e07c58a4b212a8a
Type: security-commit

## Details
fix frames deadlock with cheaters

## Patch
### poset/frame_decide.go
```diff
@@ -30,7 +30,6 @@ func (p *Poset) confirmBlock(frame idx.Frame, atropos hash.Event) (block *inter.
 	blockEvents := make([]*inter.EventHeaderData, 0, 50*p.Validators.Len())
 
 	atroposHighestBefore := p.vecClock.GetHighestBeforeAllBranches(atropos)
-	validatorIdxs := p.Validators.Idxs()
 	var highestLamport idx.Lamport
 	var lowestLamport idx.Lamport
 	var confirmedNum int
```

### poset/poset.go
```diff
@@ -246,27 +246,21 @@ func (p *Poset) calcFrameIdx(e *inter.Event, checkOnly bool) (frame idx.Frame, i
 			return selfParentFrame, false
 		}
 		// every root must be greater than prev. self-root. Instead, election will be faulty
-		isRoot = frame > selfParentFrame && (e.Frame <= 1 || p.forklessCausedByQuorumOn(e, e.Frame-1))
-		return frame, isRoot
+		// roots aren't allowed to "jump" to higher frame than selfParentFrame+1, even if they are forkless caused
+		// by 2/3W+1 there. It's because of liveness with forks, when up to 1/3W of roots on any frame may become "invisible"
+		// for forklessCause relation (so if we skip frames, there's may be deadlock when frames cannot advance because there's
+		// less than 2/3W visible roots)
+		isRoot = frame == selfParentFrame+1 && (e.Frame <= 1 || p.forklessCausedByQuorumOn(e, e.Frame-1))
+		return selfParentFrame + 1, isRoot
 	}
 
 	// calculate frame & isRoot
-	for f := maxParentsFrame + 1; f > selfParentFrame; f-- {
-		// Use the loop as a protection against forks.
-		// In more detail, forklessCause relation isn't transitive, unlike "happened-before", so we have to
-		// explicitly check forklessCausedByQuorumAt, because every root must be forkless caused by 2/3W prev roots.
-		// If there's no forks, then forklessCausedByQuorumAt always returns true for maxParentsFrame-1
-
-		if p.forklessCausedByQuorumOn(e, f-1) {
-			frame = f
-			isRoot = frame > selfParentFrame
-			return
-		}
-	}
-	// If we're here, then forklessCausedByQuorumAt returned false for every f >= selfParentFrame
 	if e.SelfParent() == nil {
 		return 1, true
 	}
+	if p.forklessCausedByQuorumOn(e, selfParentFrame) {
+		return selfParentFrame + 1, true
+	}
 	// Note: if we assign maxParentsFrame, it'll break the liveness for a case with forks, because there may be less
 	// than 2/3W possible roots at maxParentsFrame, even if 1 validator is cheater and 1/3W were offline for some time
 	// and didn't create roots at maxParentsFrame - they won't be able to create roots at maxParentsFrame because
```
