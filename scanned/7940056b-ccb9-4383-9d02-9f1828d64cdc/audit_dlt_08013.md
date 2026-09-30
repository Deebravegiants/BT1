# [?] fix(19259): Fix race condition when setting freeze round value (#19299)

## Summary
Severity: Unknown
Chain: Hedera
Component: hiero-ledger/hiero-consensus-node
Published: 2025-05-22
Source: https://github.com/hiero-ledger/hiero-consensus-node/commit/3c9eca6e6f5f020403e73eeac3e3c4d6afbab38e
Type: security-commit

## Details
fix(19259): Fix race condition when setting freeze round value (#19299)

Signed-off-by: mxtartaglia <maxi@swirldslabs.com>

## Patch
### platform-sdk/platform-apps/tests/PlatformTestingTool/src/main/java/com/swirlds/demo/platform/PlatformTestingToolConsensusStateEventHandler.java
```diff
@@ -190,7 +190,7 @@ public class PlatformTestingToolConsensusStateEventHandler
     private QuorumTriggeredAction<ControlAction> controlQuorum;
 
     /** The round number of the freeze round */
-    private long freezeRound = -1;
+    private final AtomicLong freezeRound = new AtomicLong(-1);
 
     public PlatformTestingToolConsensusStateEventHandler(@NonNull final PlatformStateFacade platformStateFacade) {
         this.platformStateFacade = platformStateFacade;
@@ -750,7 +750,7 @@ public void onHandleConsensusRound(
         round.forEachEventTransaction((event, transaction) ->
                 handleConsensusTransaction(event, transaction, state, stateSignatureTransactionCallback));
         if (platformStateFacade.isFreezeRound(state, round)) {
-            freezeRound = round.getRoundNum();
+            freezeRound.set(round.getRoundNum());
         }
     }
 
@@ -1178,7 +1178,7 @@ public boolean onSealConsensusRound(@NonNull Round round, @NonNull PlatformTesti
         // if this is a freeze round, we need to seal it
         // we cannot check the freeze time in the state at this point, because lastFrozenTime has already been updated
         // so we remember the freeze round number in onHandleConsensusRound and check it here
-        if (round.getRoundNum() == freezeRound) {
+        if (round.getRoundNum() == freezeRound.get()) {
             return true;
         }
         return round.getRoundNum() % 3 == 0;
```
