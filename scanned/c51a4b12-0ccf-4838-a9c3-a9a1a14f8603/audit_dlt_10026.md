# [?] fix: staking reentrancy.

## Summary
Severity: Unknown
Chain: Movement
Component: movement-network/movement
Published: 2024-09-02
Source: https://github.com/movement-network/movement/commit/69946e4230fad38e4ec7beda3c5b157639672287
Type: security-commit

## Details
fix: staking reentrancy.

## Patch
### protocol-units/settlement/mcr/contracts/src/staking/MovementStaking.sol
```diff
@@ -8,11 +8,13 @@ import {ICustodianToken} from "../token/custodian/CustodianToken.sol";
 import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
 import {MovementStakingStorage, EnumerableSet} from "./MovementStakingStorage.sol";
 import {IMovementStaking} from "./interfaces/IMovementStaking.sol";
+import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
 
 contract MovementStaking is
     MovementStakingStorage,
     IMovementStaking,
-    BaseStaking
+    BaseStaking,
+    ReentrancyGuard
 {
     using EnumerableSet for EnumerableSet.AddressSet;
 
@@ -24,7 +26,7 @@ contract MovementStaking is
     function registerDomain(
         uint256 epochDuration,
         address[] calldata custodians
-    ) external {
+    ) external nonReentrant {
         address domain = msg.sender;
         epochDurationByDomain[domain] = epochDuration;
 
@@ -58,7 +60,7 @@ contract MovementStaking is
         return attesters;
     }
 
-    function acceptGenesisCeremony() public {
+    function acceptGenesisCeremony() public nonReentrant {
         address domain = msg.sender;
 
         // roll over from 0 (genesis) to current epoch by block time
@@ -90,41 +92,6 @@ contract MovementStaking is
         }
     }
 
-    function setGenesisCeremony(
-        address[] calldata custodians,
-        address[] calldata attesters,
-        uint256[] calldata stakes
-    ) public {
-        address domain = msg.sender;
-        currentEpochByDomain[domain] = getEpochByBlockTime(domain);
-
-        for (uint256 i = 0; i < attesters.length; i++) {
-            address custodian = custodians[i];
-
-            // get the genesis stake for the attester
-            uint256 attesterStake = getStakeAtEpoch(
-                domain,
-                0,
-                custodian,
-                attesters[i]
-            );
-
-            // require that the stake being set is leq the genesis stake
-            if (attesterStake > stakes[i]) revert StakeExceedsGenesisStake();
-
-            // add the attester to the set
-            attestersByDomain[domain].add(attesters[i]);
-            epochStakesByDomain[domain][getCurrentEpoch(domain)][custodian][
-                attesters[i]
-            ] = stakes[i];
-            epochTotalStakeByDomain[domain][0][custodian] += stakes[i];
-
-            // transfer the outstanding stake back to the attester
-            uint256 refundAmount = stakes[i] - attesterStake;
-            _payAttester(address(this), attesters[i], custodian, refundAmount);
-        }
-    }
-
     function _addStake(
         address domain,
         uint256 epoch,
@@ -272,7 +239,7 @@ contract MovementStaking is
         address domain,
         IERC20 custodian,
         uint256 amount
-    ) external onlyRole(WHITELIST_ROLE) {
+    ) external onlyRole(WHITELIST_ROLE) nonReentrant {
         // add the attester to the list of attesters
         attestersByDomain[domain].add(msg.sender);
 
@@ -316,7 +283,7 @@ contract MovementStaking is
         address domain,
         address custodian,
         uint256 amount
-    ) external onlyRole(WHITELIST_ROLE) {
+    ) external onlyRole(WHITELIST_ROLE) nonReentrant {
         // indicate that we are going to unstake this amount in the next epoch
         // ! this doesn't actually happen until we roll over the epoch
         // note: by tracking in the next epoch we need to make sure when we roll over an epoch we check the amount rolled over from stake by the unstake in the next epoch
@@ -487,7 +454,7 @@ contract MovementStaking is
         address[] calldata attesters,
         uint256[] calldata amounts,
         uint256[] calldata refundAmounts
-    ) public {
+    ) public nonReentrant {
         for (uint256 i = 0; i < attesters.length; i++) {
             // issue a refund that is the min of the stake balance, the amount to be slashed, and the refund amount
             // this is to prevent a Domain from trying to have this contract pay out more than has been staked
@@ -566,7 +533,7 @@ contract MovementStaking is
         address[] calldata attesters,
         uint256[] calldata amounts,
         address[] calldata custodians
-    ) public {
+    ) public nonReentrant {
         // note: you may want to apply this directly to the attester's stake if the Domain sets an automatic restake policy
         for (uint256 i = 0; i < attesters.length; i++) {
             // pay the attester
```

### protocol-units/settlement/mcr/contracts/src/staking/interfaces/IMovementStaking.sol
```diff
@@ -9,11 +9,6 @@ interface IMovementStaking {
         address[] calldata custodians
     ) external;
     function acceptGenesisCeremony() external;
-    function setGenesisCeremony(
-        address[] calldata,
-        address[] calldata,
-        uint256[] calldata
-    ) external;
     function getEpochByBlockTime(address) external view returns (uint256);
     function getCurrentEpoch(address) external view returns (uint256);
     function getNextEpoch(address) external view returns (uint256);
```
