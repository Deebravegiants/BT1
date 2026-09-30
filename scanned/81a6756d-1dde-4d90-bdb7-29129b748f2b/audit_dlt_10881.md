# [?] fix: [N01]: Inconsistent usage of reentrancy protection (#4080)

## Summary
Severity: Unknown
Chain: UMA
Component: UMAprotocol/protocol
Published: 2022-08-09
Source: https://github.com/UMAprotocol/protocol/commit/ba64095d6a0dde093097df7fbd50e478c0f6cd60
Type: security-commit

## Details
fix: [N01]: Inconsistent usage of reentrancy protection (#4080)

Co-authored-by: Pablo Maldonado <pablo@umaproject.org>

## Patch
### packages/core/contracts/oracle/implementation/GovernorV2.sol
```diff
@@ -1,6 +1,7 @@
 // SPDX-License-Identifier: AGPL-3.0-only
 pragma solidity 0.8.15;
 
+import "../../common/implementation/Lockable.sol";
 import "../../common/implementation/MultiRole.sol";
 import "../interfaces/FinderInterface.sol";
 import "../interfaces/IdentifierWhitelistInterface.sol";
@@ -13,7 +14,7 @@ import "@openzeppelin/contracts/utils/Address.sol";
 /**
  * @title Takes proposals for certain governance actions and allows UMA token holders to vote on them.
  */
-contract GovernorV2 is MultiRole {
+contract GovernorV2 is MultiRole, Lockable {
     using Address for address;
 
     /****************************************
@@ -80,6 +81,7 @@ contract GovernorV2 is MultiRole {
      */
     function propose(Transaction[] memory transactions, bytes memory ancillaryData)
         external
+        nonReentrant()
         onlyRoleHolder(uint256(Roles.Proposer))
     {
         uint256 id = proposals.length;
@@ -120,7 +122,7 @@ contract GovernorV2 is MultiRole {
      * @param id unique id for the executed proposal.
      * @param transactionIndex unique transaction index for the executed proposal.
      */
-    function executeProposal(uint256 id, uint256 transactionIndex) external payable {
+    function executeProposal(uint256 id, uint256 transactionIndex) external payable nonReentrant() {
         Proposal storage proposal = proposals[id];
         int256 price =
             _getOracle().getPrice(
```

### packages/core/contracts/oracle/implementation/Staker.sol
```diff
@@ -4,14 +4,17 @@ pragma solidity ^0.8.0;
 import "../interfaces/StakerInterface.sol";
 import "../../common/interfaces/ExpandedIERC20.sol";
 
+import "./VotingToken.sol";
+import "../../common/implementation/Lockable.sol";
+
 import "@openzeppelin/contracts/access/Ownable.sol";
 import "@openzeppelin/contracts/utils/math/SafeCast.sol";
 
 /**
  * @title Staking contract enabling UMA to be locked up by stakers to earn a pro rata share of a fixed emission rate.
  * @dev Handles the staking, unstaking and reward retrieval logic.
  */
-abstract contract Staker is StakerInterface, Ownable {
+abstract contract Staker is StakerInterface, Ownable, Lockable {
     /****************************************
      *           STAKING TRACKERS           *
      ****************************************/
@@ -83,7 +86,7 @@ abstract contract Staker is StakerInterface, Ownable {
 
     event SetNewEmissionRate(uint256 newEmissionRate);
 
-    event SetNewUnstakeCooldown(uint256 newUnstakeCooldown);
+    event SetNewUnstakeCoolDown(uint256 newUnstakeCoolDown);
 
     /**
      * @notice Construct the Staker contract
@@ -110,7 +113,7 @@ abstract contract Staker is StakerInterface, Ownable {
      * be added to the pending stake. If not, the stake amount will be added to the active stake.
      * @param amount the amount of tokens to stake.
      */
-    function stake(uint256 amount) public {
+    function stake(uint256 amount) public override nonReentrant() {
         VoterStake storage voterStake = voterStakes[msg.sender];
         // If the staker has a cumulative staked balance of 0 then we can shortcut their lastRequestIndexConsidered to
         // the most recent index. This means we don't need to traverse requests where the staker was not staked.
@@ -146,7 +149,7 @@ abstract contract Staker is StakerInterface, Ownable {
      * Note that there is no way to cancel an unstake request, you must wait until after unstakeRequestTime and re-stake.
      * @param amount the amount of tokens to request to be unstaked.
      */
-    function requestUnstake(uint256 amount) public {
+    function requestUnstake(uint256 amount) external override nonReentrant() {
         require(!_inActiveReveal(), "In an active reveal phase");
         _updateTrackers(msg.sender);
         VoterStake storage voterStake = voterStakes[msg.sender];
@@ -172,7 +175,7 @@ abstract contract Staker is StakerInterface, Ownable {
      * @notice  Execute a previously requested unstake. Requires the unstake time to have passed.
      * @dev If a staker requested an unstake and time > unstakeRequestTime then send funds to staker.
      */
-    function executeUnstake() public {
+    function executeUnstake() external override nonReentrant() {
         VoterStake storage voterStake = voterStakes[msg.sender];
         require(
             voterStake.unstakeRequestTime != 0 && getCurrentTime() >= voterStake.unstakeRequestTime + unstakeCoolDown,
@@ -193,7 +196,7 @@ abstract contract Staker is StakerInterface, Ownable {
      * @notice Send accumulated rewards to the voter. Note that these rewards do not include slashing balance changes.
      * @return uint256 the amount of tokens sent to the voter.
      */
-    function withdrawRewards() public returns (uint256) {
+    function withdrawRewards() public override nonReentrant() returns (uint256) {
         _updateTrackers(msg.sender);
         VoterStake storage voterStake = voterStakes[msg.sender];
 
@@ -212,7 +215,7 @@ abstract contract Staker is StakerInterface, Ownable {
      * @dev this method requires that the user has approved this contract.
      * @return uint256 the amount of tokens that the user is staking.
      */
-    function withdrawAndRestake() external returns (uint256) {
+    function withdrawAndRestake() external nonReentrant() returns (uint256) {
         uint256 rewards = withdrawRewards();
         stake(rewards);
         return rewards;
@@ -225,21 +228,21 @@ abstract contract Staker is StakerInterface, Ownable {
     /**
      * @notice  Set the token's emission rate, the number of voting tokens that are emitted per second per staked token,
      * split pro rata to stakers.
-     * @param _emissionRate the new amount of voting tokens that are emitted per second, split pro rata to stakers.
+     * @param newEmissionRate the new amount of voting tokens that are emitted per second, split pro rata to stakers.
      */
-    function setEmissionRate(uint256 _emissionRate) external onlyOwner {
+    function setEmissionRate(uint256 newEmissionRate) external onlyOwner {
         _updateReward(address(0));
-        emissionRate = _emissionRate;
-        emit SetNewEmissionRate(emissionRate);
+        emissionRate = newEmissionRate;
+        emit SetNewEmissionRate(newEmissionRate);
     }
 
     /**
      * @notice  Set the amount of time a voter must wait to unstake after submitting a request to do so.
-     * @param _unstakeCoolDown the new duration of the cool down period in seconds.
+     * @param newUnstakeCoolDown the new duration of the cool down period in seconds.
      */
-    function setUnstakeCoolDown(uint64 _unstakeCoolDown) external onlyOwner {
-        unstakeCoolDown = _unstakeCoolDown;
-        emit SetNewUnstakeCooldown(unstakeCoolDown);
+    function setUnstakeCoolDown(uint64 newUnstakeCoolDown) external onlyOwner {
+        unstakeCoolDown = newUnstakeCoolDown;
+        emit SetNewUnstakeCoolDown(newUnstakeCoolDown);
     }
 
     function _updateTrackers(address voterAddress) internal virtual {
```

### packages/core/contracts/oracle/implementation/VotingV2.sol
```diff
@@ -302,7 +302,7 @@ contract VotingV2 is
         bytes32 identifier,
         uint256 time,
         bytes memory ancillaryData
-    ) public override onlyIfNotMigrated() onlyRegisteredContract() {
+    ) public override nonReentrant() onlyIfNotMigrated() onlyRegisteredContract() {
         _requestPrice(identifier, time, ancillaryData, false);
     }
 
@@ -494,7 +494,7 @@ contract VotingV2 is
         uint256 time,
         bytes memory ancillaryData,
         bytes32 hash
-    ) public override onlyIfNotMigrated() {
+    ) public override nonReentrant() onlyIfNotMigrated() {
         uint256 currentRoundId = voteTiming.computeCurrentRoundId(getCurrentTime());
         address voter = getVoterFromDelegate(msg.sender);
         _updateTrackers(voter);
@@ -539,7 +539,7 @@ contract VotingV2 is
         int256 price,
         bytes memory ancillaryData,
         int256 salt
-    ) public override onlyIfNotMigrated() {
+    ) public override nonReentrant() onlyIfNotMigrated() {
         // Note: computing the current round is required to disallow people from revealing an old commit after the round is over.
         uint256 currentRoundId = voteTiming.computeCurrentRoundId(getCurrentTime());
         _freezeRoundVariables(currentRoundId);
@@ -622,7 +622,7 @@ contract VotingV2 is
      * low-security available wallet for voting while keeping access to staked amounts secure by a more secure wallet.
      * @param delegate the address of the delegate.
      */
-    function setDelegate(address delegate) external {
+    function setDelegate(address delegate) external nonReentrant() {
         voterStakes[msg.sender].delegate = delegate;
     }
 
@@ -631,7 +631,7 @@ contract VotingV2 is
      * if the delegator also selected the delegate to do so (two-way relationship needed).
      * @param delegator the address of the delegator.
      */
-    function setDelegator(address delegator) external {
+    function setDelegator(address delegator) external nonReentrant() {
         delegateToStaker[msg.sender] = delegator;
     }
 
@@ -964,7 +964,7 @@ contract VotingV2 is
      * @param spamRequestIndices list of request indices to be declared as spam. Each element is a
      * pair of uint256s representing the start and end of the range.
      */
-    function signalRequestsAsSpamForDeletion(uint256[2][] calldata spamRequestIndices) external {
+    function signalRequestsAsSpamForDeletion(uint256[2][] calldata spamRequestIndices) external nonReentrant() {
         votingToken.transferFrom(msg.sender, address(this), spamDeletionProposalBond);
         uint256 currentTime = getCurrentTime();
         uint256 runningValidationIndex;
@@ -1009,7 +1009,8 @@ contract VotingV2 is
      * @notice Execute the spam deletion proposal if it has been approved by voting.
      * @param proposalId spam deletion proposal id.
      */
-    function executeSpamDeletion(uint256 proposalId) external {
+
+    function executeSpamDeletion(uint256 proposalId) external nonReentrant() {
         require(spamDeletionProposals[proposalId].executed == false);
         spamDeletionProposals[proposalId].executed = true;
 
```

### packages/core/contracts/oracle/interfaces/StakerInterface.sol
```diff
@@ -14,4 +14,10 @@ interface StakerInterface {
     function executeUnstake() external;
 
     function withdrawRewards() external returns (uint256);
+
+    function withdrawAndRestake() external returns (uint256);
+
+    function setEmissionRate(uint256 emissionRate) external;
+
+    function setUnstakeCoolDown(uint64 unstakeCoolDown) external;
 }
```
