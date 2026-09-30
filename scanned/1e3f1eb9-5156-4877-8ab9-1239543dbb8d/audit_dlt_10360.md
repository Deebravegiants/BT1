# [?] poset: fix race condition todo

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2019-10-15
Source: https://github.com/0xsoniclabs/sonic/commit/e77c1e1c8a203b6932362fcc4da1db3a2e786310
Type: security-commit

## Details
poset: fix race condition todo

## Patch
### poset/epoch.go
```diff
@@ -1,8 +1,6 @@
 package poset
 
 import (
-	"sync/atomic"
-
 	"github.com/ethereum/go-ethereum/common"
 
 	"github.com/Fantom-foundation/go-lachesis/hash"
@@ -30,17 +28,34 @@ func (p *Poset) loadEpoch() {
 
 // GetEpoch returns current epoch num to 3rd party.
 func (p *Poset) GetEpoch() idx.Epoch {
-	return idx.Epoch(atomic.LoadUint32((*uint32)(&p.EpochN)))
+	p.epochMu.Lock()
+	defer p.epochMu.Unlock()
+
+	return p.EpochN
 }
 
 // GetValidators returns validators of current epoch.
 func (p *Poset) GetValidators() pos.Validators {
+	p.epochMu.Lock()
+	defer p.epochMu.Unlock()
+
 	return p.Validators.Copy()
 }
 
 // GetEpochValidators atomically returns validators of current epoch, and the epoch.
 func (p *Poset) GetEpochValidators() (pos.Validators, idx.Epoch) {
-	return p.GetValidators(), p.GetEpoch() // TODO atomic
+	p.epochMu.Lock()
+	defer p.epochMu.Unlock()
+
+	return p.Validators.Copy(), p.EpochN
+}
+
+func (p *Poset) setEpochValidators(validators pos.Validators, epoch idx.Epoch) {
+	p.epochMu.Lock()
+	defer p.epochMu.Unlock()
+
+	p.Validators = validators
+	p.EpochN = epoch
 }
 
 // rootObservesRoot returns hash of root B, if root B forkless causes root A.
```

### poset/frame_decide.go
```diff
@@ -96,12 +96,9 @@ func (p *Poset) onNewEpoch(atropos hash.Event, lastHeaders headersByCreator) {
 	p.PrevEpoch.StateHash = p.checkpoint.StateHash
 	p.PrevEpoch.LastHeaders = lastHeaders
 
-	// new validators list
-	p.Validators = p.NextValidators.Top()
+	// new validators list, move to new epoch
+	p.setEpochValidators(p.NextValidators.Top(), p.EpochN+1)
 	p.NextValidators = p.Validators.Copy()
-
-	// move to new epoch
-	p.EpochN++
 	p.LastDecidedFrame = 0
 
 	// commit
```

### poset/poset.go
```diff
@@ -1,6 +1,7 @@
 package poset
 
 import (
+	"github.com/Fantom-foundation/go-lachesis/utils"
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/pkg/errors"
 
@@ -27,6 +28,8 @@ type Poset struct {
 
 	applyBlock inter.ApplyBlockFn
 
+	epochMu utils.SpinLock // protects p.Validators and p.EpochN
+
 	logger.Instance
 }
 
```
