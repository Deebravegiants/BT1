# [?] Fix possible int underflow when calling forkVotingResultsCursor

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2022-04-21
Source: https://github.com/radixdlt/babylon-node/commit/ef90cf676fbb588b9c01c1f12a38b9c818f63861
Type: security-commit

## Details
Fix possible int underflow when calling forkVotingResultsCursor

## Patch
### radixdlt-core/radixdlt/src/main/java/com/radixdlt/api/service/EngineStatusService.java
```diff
@@ -150,7 +150,7 @@ Optional<Long> calculateCandidateForkRemainingEpochs(long currentEpoch) {
       return Optional.empty();
     }
 
-    final var fromEpoch = currentEpoch - candidateFork.longestThresholdEpochs();
+    final var fromEpoch = Math.max(0, currentEpoch - candidateFork.longestThresholdEpochs());
 
     final var thresholdsPassingEpochs =
         Forks.calculateThresholdsPassingEpochs(
```

### radixdlt-core/radixdlt/src/main/java/com/radixdlt/statecomputer/forks/Forks.java
```diff
@@ -315,7 +315,7 @@ Optional<Long> findExecuteEpochForCandidate(ForksEpochStore forksEpochStore) {
     final var candidateFork = maybeCandidateFork.get();
     final var candidateForkId = CandidateForkVote.candidateForkId(candidateFork);
 
-    final var fromEpoch = candidateFork.minEpoch() - candidateFork.longestThresholdEpochs();
+    final var fromEpoch = Math.max(0, candidateFork.minEpoch() - candidateFork.longestThresholdEpochs());
     final var toEpoch =
         candidateFork.maxEpoch() + 1 < candidateFork.maxEpoch() // Check for overflows
             ? Long.MAX_VALUE
@@ -446,7 +446,7 @@ public static boolean shouldCandidateForkBeEnacted(
       return false;
     }
 
-    final var fromEpoch = nextEpoch - candidateFork.longestThresholdEpochs();
+    final var fromEpoch = Math.max(0, nextEpoch - candidateFork.longestThresholdEpochs());
     try (final var previousVotingResultsCursor =
         forksEpochStore.forkVotingResultsCursor(
             fromEpoch, candidateFork.maxEpoch(), candidateForkId)) {
```
