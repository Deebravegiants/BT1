# [?] fix(protocol): avoid span overflow by limitting aggregation (#20828)

## Summary
Severity: Unknown
Chain: Taiko
Component: taikoxyz/taiko-mono
Published: 2025-11-28
Source: https://github.com/taikoxyz/taiko-mono/commit/42e2a51608487a70bae2ef89b38e02292bdc44e4
Type: security-commit

## Details
fix(protocol): avoid span overflow by limitting aggregation (#20828)

Co-authored-by: Gustavo Gonzalez <gustavo@taiko.xyz>
Co-authored-by: ggonzalez94 <17907743+ggonzalez94@users.noreply.github.com>
Co-authored-by: Daniel Wang <99078276+dantaik@users.noreply.github.com>

## Patch
### packages/protocol/contracts/layer1/core/impl/InboxOptimized1.sol
```diff
@@ -186,7 +186,11 @@ contract InboxOptimized1 is Inbox {
             // Process remaining proposals with optimized loop
             for (uint256 i = 1; i < _input.proposals.length; ++i) {
                 // Check for consecutive proposal aggregation
-                if (_input.proposals[i].id == currentGroupStartId + currentRecord.span) {
+                // Cap at 255 proposals per record to prevent uint8 span overflow
+                if (
+                    _input.proposals[i].id == currentGroupStartId + currentRecord.span
+                        && currentRecord.span < type(uint8).max
+                ) {
                     TransitionRecord memory nextRecord = _buildTransitionRecord(
                         _input.proposals[i], _input.transitions[i], _input.metadata[i]
                     );
```

### packages/protocol/gas-reports/layer1-contracts.txt
```diff
@@ -157,14 +157,14 @@ InboxOptimized1Finalize:test_finalize_processesBondInstructions() (gas: 445692)
 InboxOptimized1Finalize:test_finalize_singleProposal() (gas: 440098)
 InboxOptimized1Finalize:test_finalize_stopsWhenProposalNotProven() (gas: 539095)
 InboxOptimized1Finalize:test_finalize_twoProposals() (gas: 645132)
-InboxOptimized1Finalize:test_finalize_updatesLastFinalizedAcrossAggregatedSpan() (gas: 568473)
-InboxOptimized1Init:test_activate_RevertWhen_NotInitialized() (gas: 4381078)
-InboxOptimized1Init:test_activate_RevertWhen_UnauthorizedCaller() (gas: 4455325)
-InboxOptimized1Init:test_activate_SucceedsWhenCalledTwice() (gas: 4526375)
-InboxOptimized1Init:test_activate_succeeds() (gas: 4535533)
-InboxOptimized1Init:test_init_RevertWhen_CalledTwice() (gas: 4453766)
-InboxOptimized1Init:test_init_setsOwnerToCallerWhenOwnerZero() (gas: 4452868)
-InboxOptimized1Init:test_init_succeeds() (gas: 4453153)
+InboxOptimized1Finalize:test_finalize_updatesLastFinalizedAcrossAggregatedSpan() (gas: 568519)
+InboxOptimized1Init:test_activate_RevertWhen_NotInitialized() (gas: 4384478)
+InboxOptimized1Init:test_activate_RevertWhen_UnauthorizedCaller() (gas: 4458725)
+InboxOptimized1Init:test_activate_SucceedsWhenCalledTwice() (gas: 4529775)
+InboxOptimized1Init:test_activate_succeeds() (gas: 4538933)
+InboxOptimized1Init:test_init_RevertWhen_CalledTwice() (gas: 4457166)
+InboxOptimized1Init:test_init_setsOwnerToCallerWhenOwnerZero() (gas: 4456268)
+InboxOptimized1Init:test_init_succeeds() (gas: 4456553)
 InboxOptimized1MultipleBlobsTest:test_InboxOptimized1_propose_withMultipleBlobs() (gas: 201726)
 InboxOptimized1MultipleBlobsTest:test_getCurrentForcedInclusionFee_EmptyQueue() (gas: 24936)
 InboxOptimized1MultipleBlobsTest:test_getCurrentForcedInclusionFee_IncreasesWithQueue() (gas: 444204)
@@ -215,14 +215,14 @@ InboxOptimized1Propose:test_saveForcedInclusion_RevertWhen_FirstProposalMissing(
 InboxOptimized1Prove:test_prove_RevertWhen_EmptyProposals() (gas: 34674)
 InboxOptimized1Prove:test_prove_RevertWhen_InconsistentParams() (gas: 40105)
 InboxOptimized1Prove:test_prove_RevertWhen_ProposalNotFound() (gas: 67893)
-InboxOptimized1Prove:test_prove_fiveConsecutiveProposals() (gas: 806637)
-InboxOptimized1Prove:test_prove_mixed_consecutiveAndGaps() (gas: 1010597)
-InboxOptimized1Prove:test_prove_nonConsecutive_multipleGaps() (gas: 888808)
-InboxOptimized1Prove:test_prove_nonConsecutive_singleGap() (gas: 587073)
-InboxOptimized1Prove:test_prove_reverseOrder() (gas: 671876)
+InboxOptimized1Prove:test_prove_fiveConsecutiveProposals() (gas: 806821)
+InboxOptimized1Prove:test_prove_mixed_consecutiveAndGaps() (gas: 1010758)
+InboxOptimized1Prove:test_prove_nonConsecutive_multipleGaps() (gas: 888854)
+InboxOptimized1Prove:test_prove_nonConsecutive_singleGap() (gas: 587096)
+InboxOptimized1Prove:test_prove_reverseOrder() (gas: 671922)
 InboxOptimized1Prove:test_prove_singleProposal() (gas: 287643)
-InboxOptimized1Prove:test_prove_threeConsecutiveProposals() (gas: 541636)
-InboxOptimized1Prove:test_prove_twoConsecutiveProposals() (gas: 411116)
+InboxOptimized1Prove:test_prove_threeConsecutiveProposals() (gas: 541728)
+InboxOptimized1Prove:test_prove_twoConsecutiveProposals() (gas: 411162)
 InboxOptimized1Prove:test_prove_withCustomDesignatedProver() (gas: 274242)
 InboxOptimized1TransitionRecord:test_storeTransitionRecord_conflictDetection_ringBuffer() (gas: 346201)
 InboxOptimized1TransitionRecord:test_storeTransitionRecord_differentPartialParent_compositeKeyFallback() (gas: 348907)
@@ -241,14 +241,14 @@ InboxOptimized2Finalize:test_finalize_processesBondInstructions() (gas: 433773)
 InboxOptimized2Finalize:test_finalize_singleProposal() (gas: 427733)
 InboxOptimized2Finalize:test_finalize_stopsWhenProposalNotProven() (gas: 520454)
 InboxOptimized2Finalize:test_finalize_twoProposals() (gas: 625515)
-InboxOptimized2Finalize:test_finalize_updatesLastFinalizedAcrossAggregatedSpan() (gas: 549650)
-InboxOptimized2Init:test_activate_RevertWhen_NotInitialized() (gas: 4875594)
-InboxOptimized2Init:test_activate_RevertWhen_UnauthorizedCaller() (gas: 4949841)
-InboxOptimized2Init:test_activate_SucceedsWhenCalledTwice() (gas: 5013821)
-InboxOptimized2Init:test_activate_succeeds() (gas: 5013593)
-InboxOptimized2Init:test_init_RevertWhen_CalledTwice() (gas: 4948282)
-InboxOptimized2Init:test_init_setsOwnerToCallerWhenOwnerZero() (gas: 4947384)
-InboxOptimized2Init:test_init_succeeds() (gas: 4947669)
+InboxOptimized2Finalize:test_finalize_updatesLastFinalizedAcrossAggregatedSpan() (gas: 549696)
+InboxOptimized2Init:test_activate_RevertWhen_NotInitialized() (gas: 4879003)
+InboxOptimized2Init:test_activate_RevertWhen_UnauthorizedCaller() (gas: 4953250)
+InboxOptimized2Init:test_activate_SucceedsWhenCalledTwice() (gas: 5017230)
+InboxOptimized2Init:test_activate_succeeds() (gas: 5017002)
+InboxOptimized2Init:test_init_RevertWhen_CalledTwice() (gas: 4951691)
+InboxOptimized2Init:test_init_setsOwnerToCallerWhenOwnerZero() (gas: 4950793)
+InboxOptimized2Init:test_init_succeeds() (gas: 4951078)
 InboxOptimized2Propose:test_getCurrentForcedInclusionFee_EmptyQueue() (gas: 24936)
 InboxOptimized2Propose:test_getCurrentForcedInclusionFee_IncreasesWithQueue() (gas: 438310)
 InboxOptimized2Propose:test_getCurrentForcedInclusionFee_MatchesCalculation() (gas: 824010)
@@ -275,14 +275,14 @@ InboxOptimized2Propose:test_saveForcedInclusion_RevertWhen_FirstProposalMissing(
 InboxOptimized2Prove:test_prove_RevertWhen_EmptyProposals() (gas: 34887)
 InboxOptimized2Prove:test_prove_RevertWhen_InconsistentParams() (gas: 24139)
 InboxOptimized2Prove:test_prove_RevertWhen_ProposalNotFound() (gas: 69658)
-InboxOptimized2Prove:test_prove_fiveConsecutiveProposals() (gas: 789368)
-InboxOptimized2Prove:test_prove_mixed_consecutiveAndGaps() (gas: 986698)
-InboxOptimized2Prove:test_prove_nonConsecutive_multipleGaps() (gas: 865377)
-InboxOptimized2Prove:test_prove_nonConsecutive_singleGap() (gas: 573079)
-InboxOptimized2Prove:test_prove_reverseOrder() (gas: 657077)
+InboxOptimized2Prove:test_prove_fiveConsecutiveProposals() (gas: 789552)
+InboxOptimized2Prove:test_prove_mixed_consecutiveAndGaps() (gas: 986859)
+InboxOptimized2Prove:test_prove_nonConsecutive_multipleGaps() (gas: 865423)
+InboxOptimized2Prove:test_prove_nonConsecutive_singleGap() (gas: 573102)
+InboxOptimized2Prove:test_prove_reverseOrder() (gas: 657123)
 InboxOptimized2Prove:test_prove_singleProposal() (gas: 282688)
-InboxOptimized2Prove:test_prove_threeConsecutiveProposals() (gas: 531081)
-InboxOptimized2Prove:test_prove_twoConsecutiveProposals() (gas: 403292)
+InboxOptimized2Prove:test_prove_threeConsecutiveProposals() (gas: 531173)
+InboxOptimized2Prove:test_prove_twoConsecutiveProposals() (gas: 403338)
 InboxOptimized2Prove:test_prove_withCustomDesignatedProver() (gas: 269438)
 InboxPropose:test_getCurrentForcedInclusionFee_EmptyQueue() (gas: 24936)
 InboxPropose:test_getCurrentForcedInclusionFee_IncreasesWithQueue() (gas: 444232)
```

### packages/protocol/snapshots/shasta-prove.json
```diff
@@ -1,25 +1,25 @@
 {
   "prove_consecutive_2_Inbox": "77308",
-  "prove_consecutive_2_InboxOptimized1": "69681",
-  "prove_consecutive_2_InboxOptimized2": "66141",
+  "prove_consecutive_2_InboxOptimized1": "69727",
+  "prove_consecutive_2_InboxOptimized2": "66187",
   "prove_consecutive_3_Inbox": "112601",
-  "prove_consecutive_3_InboxOptimized1": "75280",
-  "prove_consecutive_3_InboxOptimized2": "71798",
+  "prove_consecutive_3_InboxOptimized1": "75372",
+  "prove_consecutive_3_InboxOptimized2": "71890",
   "prove_consecutive_5_Inbox": "183452",
-  "prove_consecutive_5_InboxOptimized1": "86686",
-  "prove_consecutive_5_InboxOptimized2": "82676",
+  "prove_consecutive_5_InboxOptimized1": "86870",
+  "prove_consecutive_5_InboxOptimized2": "82860",
   "prove_gaps_1_Inbox": "77377",
-  "prove_gaps_1_InboxOptimized1": "121510",
-  "prove_gaps_1_InboxOptimized2": "116076",
+  "prove_gaps_1_InboxOptimized1": "121533",
+  "prove_gaps_1_InboxOptimized2": "116099",
   "prove_gaps_2_Inbox": "112782",
-  "prove_gaps_2_InboxOptimized1": "178996",
-  "prove_gaps_2_InboxOptimized2": "171701",
+  "prove_gaps_2_InboxOptimized1": "179042",
+  "prove_gaps_2_InboxOptimized2": "171747",
   "prove_mixed_groups_Inbox": "183637",
-  "prove_mixed_groups_InboxOptimized1": "138649",
-  "prove_mixed_groups_InboxOptimized2": "132693",
+  "prove_mixed_groups_InboxOptimized1": "138810",
+  "prove_mixed_groups_InboxOptimized2": "132854",
   "prove_reverse_Inbox": "112626",
-  "prove_reverse_InboxOptimized1": "178851",
-  "prove_reverse_InboxOptimized2": "171629",
+  "prove_reverse_InboxOptimized1": "178897",
+  "prove_reverse_InboxOptimized2": "171675",
   "prove_single_Inbox": "44177",
   "prove_single_InboxOptimized1": "66086",
   "prove_single_InboxOptimized2": "62806"
```
