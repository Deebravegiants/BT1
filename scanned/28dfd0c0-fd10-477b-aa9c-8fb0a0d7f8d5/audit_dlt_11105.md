# [?] fix dos attack vulnerability

## Summary
Severity: Unknown
Chain: Morph
Component: morph-l2/morph
Published: 2024-10-23
Source: https://github.com/morph-l2/morph/commit/6cc2a43e14c6250c9af3b1249069be44d83fb43d
Type: security-commit

## Details
fix dos attack vulnerability

## Patch
### contracts/contracts/l2/staking/Gov.sol
```diff
@@ -61,6 +61,9 @@ contract Gov is IGov, OwnableUpgradeable {
     /// @notice proposal voter info
     mapping(uint256 proposalID => EnumerableSetUpgradeable.AddressSet) internal votes;
 
+    /// @notice latest passed proposal ID
+    uint256 public latestPassedProposalID;
+
     /**********************
      * Function Modifiers *
      **********************/
@@ -146,6 +149,7 @@ contract Gov is IGov, OwnableUpgradeable {
     /// @notice vote a proposal
     function vote(uint256 proposalID) external onlySequencer {
         require(proposalID <= currentProposalID, "invalid proposalID");
+        require(proposalID > latestPassedProposalID, "expired proposal");
         require(proposalID >= undeletedProposalStart, "proposal pruned");
         uint256 expirationTime = proposalInfos[proposalID].expirationTime;
         require(
@@ -160,6 +164,7 @@ contract Gov is IGov, OwnableUpgradeable {
         }
     }
 
+    /// @notice set voting duration
     function setVotingDuration(uint256 _votingDuration) external onlyOwner {
         require(_votingDuration > 0 && _votingDuration != votingDuration, "invalid new proposal voting duration");
         uint256 _oldVotingDuration = votingDuration;
@@ -180,13 +185,27 @@ contract Gov is IGov, OwnableUpgradeable {
         _executeProposal(proposalID);
     }
 
+    /// @notice execute a passed proposal
+    /// @param deleteTo      last proposal ID to delete
+    function cleanUpExpiredProposals(uint256 deleteTo) external {
+        require(deleteTo < latestPassedProposalID, "only allow to delete the proposal befor latest passed proposal");
+        // when a proposal is passed, the previous proposals will be invalidated and deleted
+        for (uint256 i = undeletedProposalStart; i <= deleteTo; i++) {
+            delete proposalData[i];
+            delete proposalInfos[i];
+            delete votes[i];
+        }
+        undeletedProposalStart = deleteTo + 1;
+    }
+
     /*************************
      * Public View Functions *
      *************************/
 
     /// @notice return proposal status. {finished, passed, executed}
     function proposalStatus(uint256 proposalID) public view returns (bool, bool, bool) {
         require(proposalID <= currentProposalID, "invalid proposalID");
+        require(proposalID > latestPassedProposalID, "expired proposal");
         require(proposalID >= undeletedProposalStart, "proposal pruned");
         bool executed = proposalInfos[proposalID].executed;
         uint256 expirationTime = proposalInfos[proposalID].expirationTime;
@@ -210,6 +229,8 @@ contract Gov is IGov, OwnableUpgradeable {
 
     /// @notice execute a passed proposal
     function _executeProposal(uint256 proposalID) internal {
+        latestPassedProposalID = proposalID;
+
         if (batchBlockInterval != proposalData[proposalID].batchBlockInterval) {
             uint256 _oldValue = batchBlockInterval;
             batchBlockInterval = proposalData[proposalID].batchBlockInterval;
@@ -228,14 +249,6 @@ contract Gov is IGov, OwnableUpgradeable {
         }
         proposalInfos[proposalID].executed = true;
 
-        // when a proposal is passed, the previous proposals will be invalidated and deleted
-        for (uint256 i = undeletedProposalStart; i < proposalID; i++) {
-            delete proposalData[i];
-            delete proposalInfos[i];
-            delete votes[i];
-        }
-        undeletedProposalStart = proposalID;
-
         emit ProposalExecuted(proposalID, batchBlockInterval, batchTimeout, rollupEpoch);
     }
 
```
