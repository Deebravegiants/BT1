# [?] Merge #6924: fix: potential race condition in `ProcessNewChainLock`

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2025-11-03
Source: https://github.com/dashpay/dash/commit/be4a71cb23d77cf46d24b1fd6c83f54fd345698b
Type: security-commit

## Details
Merge #6924: fix: potential race condition in `ProcessNewChainLock`

696b926504be4ce6ccc5031c605d6d79e37356aa fix: potential race condition in ProcessNewChainLock (UdjinM6)

Pull request description:

  ## Issue being fixed or feature implemented
  `ProcessNewChainLock` can be called from 2 threads: `sigshares` (when `clsig` is created locally from recovered sigs) and `msghand` (when `clsig` is received from another peer). Suppose there is a node is at some height `h` and 2 blocks come very fast. The node would create `clsig` for the best block (`h+2`) but it could also receive `clsig` for the previous one (`h+1`) from other peers. We release `cs` temporary in `ProcessNewChainLock` so both `clsig(h+1)` and `clsig(h+2)` could enter `ProcessNewChainLock` and pass height check `h <  h+1` and `h < h+2` until they are blocked by `cs_main`. If `clsig(h+2)` was the first in the queue it will move to the next part and assign `bestChainLock` = `clsig(h+2)` but once the lock is released `clsig(h+1)` will move forward and assign `bestChainLock` = `clsig(h+1)`.

  This is highly unlikely to happen on live networks but it does cause issues on regtest sometimes when we wait for a specific chainlocked block (`h+2`) but the peer won't relay it cause it's not the one the peer thinks is the best (`h+1`), all we get is `notfound`.

  ## What was done?
  Re-verify clsig height once we lock it again

  ## How Has This Been Tested?
  I had this issue in `feature_governance_cl.py` and now it's gone

  ## Breaking Changes
  n/a

  ## Checklist:
  - [ ] I have performed a self-review of my own code
  - [ ] I have commented my code, particularly in hard-to-understand areas
  - [ ] I have added or updated relevant unit/integration/functional/e2e tests
  - [ ] I have made corresponding changes to the documentation
  - [ ] I have assigned this pull request to a milestone _(for repository code-owners and collaborators only)_

ACKs for top commit:
  PastaPastaPasta:
    utACK 696b926504be4ce6ccc5031c605d6d79e37356aa
  knst:
    utACK 696b926504be4ce6ccc5031c605d6d79e37356aa

Tree-SHA512: 1dc87b1d71f7fb1f45c09f05144d50b78d0a6fd3e539c5c4bea0fd394d6cc29bd97713e975ef6256548f29b42f7adace47e10cbcbe2abae859ae23913a848e25

## Patch
### src/chainlock/chainlock.cpp
```diff
@@ -135,7 +135,7 @@ MessageProcessingResult CChainLocksHandler::ProcessNewChainLock(const NodeId fro
         }
 
         if (!bestChainLock.IsNull() && clsig.getHeight() <= bestChainLock.getHeight()) {
-            // no need to process/relay older CLSIGs
+            // no need to process older/same CLSIGs
             return {};
         }
     }
@@ -154,6 +154,11 @@ MessageProcessingResult CChainLocksHandler::ProcessNewChainLock(const NodeId fro
 
     {
         LOCK(cs);
+        // newer chainlock could be processed via another thread while we were not holding the lock, re-verify
+        if (!bestChainLock.IsNull() && clsig.getHeight() <= bestChainLock.getHeight()) {
+            // no need to process older/same CLSIGs
+            return {};
+        }
         bestChainLockHash = hash;
         bestChainLock = clsig;
 
```
