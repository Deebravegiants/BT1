# [?] fix: MCR reentrancy.

## Summary
Severity: Unknown
Chain: Movement
Component: movement-network/movement
Published: 2024-09-02
Source: https://github.com/movement-network/movement/commit/54c3f17cd6c52d0ef2c81eaefdc740d730a6f39a
Type: security-commit

## Details
fix: MCR reentrancy.

## Patch
### protocol-units/settlement/mcr/contracts/src/settlement/MCR.sol
```diff
@@ -8,8 +8,15 @@ import {MovementStaking, IMovementStaking} from "../staking/MovementStaking.sol"
 import {MCRStorage} from "./MCRStorage.sol";
 import {BaseSettlement} from "./settlement/BaseSettlement.sol";
 import {IMCR} from "./interfaces/IMCR.sol";
-
-contract MCR is Initializable, BaseSettlement, MCRStorage, IMCR {
+import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
+
+contract MCR is
+    Initializable,
+    BaseSettlement,
+    MCRStorage,
+    ReentrancyGuard,
+    IMCR
+{
     function initialize(
         IMovementStaking _stakingContract,
         uint256 _lastAcceptedBlockHeight,
@@ -25,11 +32,11 @@ contract MCR is Initializable, BaseSettlement, MCRStorage, IMCR {
     }
 
     // creates a commitment
-    function createBlockCommitment(uint256 height, bytes32 commitment, bytes32 blockId)
-        public
-        pure
-        returns (BlockCommitment memory)
-    {
+    function createBlockCommitment(
+        uint256 height,
+        bytes32 commitment,
+        bytes32 blockId
+    ) public pure returns (BlockCommitment memory) {
         return BlockCommitment(height, commitment, blockId);
     }
 
@@ -54,13 +61,28 @@ contract MCR is Initializable, BaseSettlement, MCRStorage, IMCR {
     }
 
     // gets the stake for a given attester at a given epoch
-    function getStakeAtEpoch(uint256 epoch, address custodian, address attester) public view returns (uint256) {
-        return stakingContract.getStakeAtEpoch(address(this), epoch, custodian, attester);
+    function getStakeAtEpoch(
+        uint256 epoch,
+        address custodian,
+        address attester
+    ) public view returns (uint256) {
+        return
+            stakingContract.getStakeAtEpoch(
+                address(this),
+                epoch,
+                custodian,
+                attester
+            );
     }
 
     // todo: memoize this
-    function computeAllStakeAtEpoch(uint256 epoch, address attester) public view returns (uint256) {
-        address[] memory custodians = stakingContract.getCustodiansByDomain(address(this));
+    function computeAllStakeAtEpoch(
+        uint256 epoch,
+        address attester
+    ) public view returns (uint256) {
+        address[] memory custodians = stakingContract.getCustodiansByDomain(
+            address(this)
+        );
         uint256 totalStake = 0;
         for (uint256 i = 0; i < custodians.length; i++) {
             // for now, each custodian has weight of 1
@@ -70,25 +92,42 @@ contract MCR is Initializable, BaseSettlement, MCRStorage, IMCR {
     }
 
     // gets the stake for a given attester at the current epoch
-    function getCurrentEpochStake(address custodian, address attester) public view returns (uint256) {
+    function getCurrentEpochStake(
+        address custodian,
+        address attester
+    ) public view returns (uint256) {
         return getStakeAtEpoch(getCurrentEpoch(), custodian, attester);
     }
 
-    function computeAllCurrentEpochStake(address attester) public view returns (uint256) {
+    function computeAllCurrentEpochStake(
+        address attester
+    ) public view returns (uint256) {
         return computeAllStakeAtEpoch(getCurrentEpoch(), attester);
     }
 
     // gets the total stake for a given epoch
-    function getTotalStakeForEpoch(uint256 epoch, address custodian) public view returns (uint256) {
-        return stakingContract.getTotalStakeForEpoch(address(this), epoch, custodian);
+    function getTotalStakeForEpoch(
+        uint256 epoch,
+        address custodian
+    ) public view returns (uint256) {
+        return
+            stakingContract.getTotalStakeForEpoch(
+                address(this),
+                epoch,
+                custodian
+            );
     }
 
     function acceptGenesisCeremony() public onlyRole(DEFAULT_ADMIN_ROLE) {
         stakingContract.acceptGenesisCeremony();
     }
 
-    function computeAllTotalStakeForEpoch(uint256 epoch) public view returns (uint256) {
-        address[] memory custodians = stakingContract.getCustodiansByDomain(address(this));
+    function computeAllTotalStakeForEpoch(
+        uint256 epoch
+    ) public view returns (uint256) {
+        address[] memory custodians = stakingContract.getCustodiansByDomain(
+            address(this)
+        );
         uint256 totalStake = 0;
         for (uint256 i = 0; i < custodians.length; i++) {
             // for now, each custodian has weight of 1
@@ -98,55 +137,79 @@ contract MCR is Initializable, BaseSettlement, MCRStorage, IMCR {
     }
 
     // gets the total stake for the current epoch
-    function getTotalStakeForCurrentEpoch(address custodian) public view returns (uint256) {
+    function getTotalStakeForCurrentEpoch(
+        address custodian
+    ) public view returns (uint256) {
         return getTotalStakeForEpoch(getCurrentEpoch(), custodian);
     }
 
-    function computeAllTotalStakeForCurrentEpoch() public view returns (uint256) {
-        return computeAllTotalStakeForEpoch(getCurrentEpoch());
-    }
-
-    function getValidatorCommitmentAtBlockHeight(uint256 height, address attester)
+    function computeAllTotalStakeForCurrentEpoch()
         public
         view
-        returns (BlockCommitment memory)
+        returns (uint256)
     {
+        return computeAllTotalStakeForEpoch(getCurrentEpoch());
+    }
+
+    function getValidatorCommitmentAtBlockHeight(
+        uint256 height,
+        address attester
+    ) public view returns (BlockCommitment memory) {
         return commitments[height][attester];
     }
 
-    function getAcceptedCommitmentAtBlockHeight(uint256 height) public view returns (BlockCommitment memory) {
+    function getAcceptedCommitmentAtBlockHeight(
+        uint256 height
+    ) public view returns (BlockCommitment memory) {
         return acceptedBlocks[height];
     }
 
     function getAttesters() public view returns (address[] memory) {
         return stakingContract.getAttestersByDomain(address(this));
     }
 
-    // commits a attester to a particular block
-    function submitBlockCommitmentForAttester(address attester, BlockCommitment memory blockCommitment) internal {
+    /**
+     * @dev submits a block commitment for an attester.
+     */
+    function submitBlockCommitmentForAttester(
+        address attester,
+        BlockCommitment memory blockCommitment
+    ) internal {
         // Attester has already committed to a block at this height
-        if (commitments[blockCommitment.height][attester].height != 0) revert AttesterAlreadyCommitted();
+        if (commitments[blockCommitment.height][attester].height != 0)
+            revert AttesterAlreadyCommitted();
 
         // note: do no uncomment the below, we want to allow this in case we have lagging attesters
         // Attester has committed to an already accepted block
         // if ( lastAcceptedBlockHeight > blockCommitment.height) revert AlreadyAcceptedBlock();
         // Attester has committed to a block too far ahead of the last accepted block
-        if (lastAcceptedBlockHeight + leadingBlockTolerance < blockCommitment.height) revert AttesterAlreadyCommitted();
+        if (
+            lastAcceptedBlockHeight + leadingBlockTolerance <
+            blockCommitment.height
+        ) revert AttesterAlreadyCommitted();
 
         // assign the block height to the current epoch if it hasn't been assigned yet
         if (blockHeightEpochAssignments[blockCommitment.height] == 0) {
             // note: this is an intended race condition, but it is benign because of the tolerance
-            blockHeightEpochAssignments[blockCommitment.height] = getEpochByBlockTime();
+            blockHeightEpochAssignments[
+                blockCommitment.height
+            ] = getEpochByBlockTime();
         }
 
         // register the attester's commitment
         commitments[blockCommitment.height][attester] = blockCommitment;
 
         // increment the commitment count by stake
         uint256 allCurrentEpochStake = computeAllCurrentEpochStake(attester);
-        commitmentStakes[blockCommitment.height][blockCommitment.commitment] += allCurrentEpochStake;
+        commitmentStakes[blockCommitment.height][
+            blockCommitment.commitment
+        ] += allCurrentEpochStake;
 
-        emit BlockCommitmentSubmitted(blockCommitment.blockId, blockCommitment.commitment, allCurrentEpochStake);
+        emit BlockCommitmentSubmitted(
+            blockCommitment.blockId,
+            blockCommitment.commitment,
+            allCurrentEpochStake
+        );
 
         // keep ticking through to find accepted blocks
         // note: this is what allows for batching to be successful
@@ -157,6 +220,8 @@ contract MCR is Initializable, BaseSettlement, MCRStorage, IMCR {
         while (tickOnBlockHeight(lastAcceptedBlockHeight + 1)) {}
     }
 
+    /**
+     */
     function tickOnBlockHeight(uint256 blockHeight) internal returns (bool) {
         // get the epoch assigned to the block height
         uint256 blockEpoch = blockHeightEpochAssignments[blockHeight];
@@ -170,18 +235,23 @@ contract MCR is Initializable, BaseSettlement, MCRStorage, IMCR {
 
         // note: we could keep track of seen commitments in a set
         // but since the operations we're doing are very cheap, the set actually adds overhead
-        uint256 supermajority = (2 * computeAllTotalStakeForEpoch(blockEpoch)) / 3;
+        uint256 supermajority = (2 * computeAllTotalStakeForEpoch(blockEpoch)) /
+            3;
         address[] memory attesters = getAttesters();
 
         // iterate over the attester set
         for (uint256 i = 0; i < attesters.length; i++) {
             address attester = attesters[i];
 
             // get a commitment for the attester at the block height
-            BlockCommitment memory blockCommitment = commitments[blockHeight][attester];
+            BlockCommitment memory blockCommitment = commitments[blockHeight][
+                attester
+            ];
 
             // check the total stake on the commitment
-            uint256 totalStakeOnCommitment = commitmentStakes[blockCommitment.height][blockCommitment.commitment];
+            uint256 totalStakeOnCommitment = commitmentStakes[
+                blockCommitment.height
+            ][blockCommitment.commitment];
 
             if (totalStakeOnCommitment > supermajority) {
                 // accept the block commitment (this may trigger a roll over of the epoch)
@@ -195,21 +265,35 @@ contract MCR is Initializable, BaseSettlement, MCRStorage, IMCR {
         return false;
     }
 
-    function submitBlockCommitment(BlockCommitment memory blockCommitment) public {
+    /**
+     * @dev There is no reason for this to be reentrant, so it is marked as nonReentrant.
+     */
+    function submitBlockCommitment(
+        BlockCommitment memory blockCommitment
+    ) public nonReentrant {
         submitBlockCommitmentForAttester(msg.sender, blockCommitment);
     }
 
-    function submitBatchBlockCommitment(BlockCommitment[] memory blockCommitments) public {
+    function submitBatchBlockCommitment(
+        BlockCommitment[] memory blockCommitments
+    ) public {
         for (uint256 i = 0; i < blockCommitments.length; i++) {
             submitBlockCommitment(blockCommitments[i]);
         }
     }
 
-    function _acceptBlockCommitment(BlockCommitment memory blockCommitment) internal {
+    /**
+     * @dev Accepts a block commitment.
+     * @dev Under the current implementation this shares in recursion with the tickOnBlockHeight, so it should be reentrant.
+     */
+    function _acceptBlockCommitment(
+        BlockCommitment memory blockCommitment
+    ) internal {
         uint256 currentEpoch = getCurrentEpoch();
         // get the epoch for the block commitment
         //  Block commitment is not in the current epoch, it cannot be accepted. This indicates a bug in the protocol.
-        if (blockHeightEpochAssignments[blockCommitment.height] != currentEpoch) revert UnacceptableBlockCommitment();
+        if (blockHeightEpochAssignments[blockCommitment.height] != currentEpoch)
+            revert UnacceptableBlockCommitment();
 
         // set accepted block commitment
         acceptedBlocks[blockCommitment.height] = blockCommitment;
@@ -221,20 +305,28 @@ contract MCR is Initializable, BaseSettlement, MCRStorage, IMCR {
         slashMinority(blockCommitment);
 
         // emit the block accepted event
-        emit BlockAccepted(blockCommitment.blockId, blockCommitment.commitment, blockCommitment.height);
+        emit BlockAccepted(
+            blockCommitment.blockId,
+            blockCommitment.commitment,
+            blockCommitment.height
+        );
 
         // if the timestamp epoch is greater than the current epoch, roll over the epoch
         if (getEpochByBlockTime() > currentEpoch) {
             rollOverEpoch();
         }
     }
 
+    /**
+     */
     function slashMinority(BlockCommitment memory blockCommitment) internal {
         // stakingContract.slash(custodians, attesters, amounts, refundAmounts);
     }
 
+    /**
+     * @dev nonReentrant because there is no need to reenter this function. It should be called iteratively. Marked on the internal method to simplify risks from complex calling patterns. This also calls an external contract.
+     */
     function rollOverEpoch() internal {
-        console.log("Rolling over epoch %s", getCurrentEpoch());
         stakingContract.rollOverEpoch();
     }
 }
```
