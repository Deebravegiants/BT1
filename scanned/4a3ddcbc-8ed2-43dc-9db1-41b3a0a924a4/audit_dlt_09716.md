# [?] fix: deprecate oz reentrancy and replace with solady transient reentrancy

## Summary
Severity: Unknown
Chain: EtherFi
Component: etherfi-protocol/smart-contracts
Published: 2026-06-02
Source: https://github.com/etherfi-protocol/smart-contracts/commit/053c41d09e99abcf11ac20a2bdec4530edfea3e9
Type: security-commit

## Details
fix: deprecate oz reentrancy and replace with solady transient reentrancy

## Patch
### src/core/LiquidityPool.sol
```diff
@@ -16,11 +16,11 @@ import "@etherfi/staking/interfaces/IEtherFiNodesManager.sol";
 import "@etherfi/withdrawals/interfaces/IEtherFiRedemptionManager.sol";
 import "@etherfi/withdrawals/interfaces/IPriorityWithdrawalQueue.sol";
 import "@etherfi/governance/interfaces/IBlacklister.sol";
-import "@etherfi/governance/utils/ReentrancyGuardNamespaced.sol";
+import {ReentrancyGuardTransient} from "solady/utils/ReentrancyGuardTransient.sol";
 import "@etherfi/governance/utils/RolesLibrary.sol";
 import "@etherfi/governance/utils/PausableUntil.sol";
 
-contract LiquidityPool is Initializable, OwnableUpgradeable, UUPSUpgradeable, ReentrancyGuardNamespaced, PausableUntil, ILiquidityPool {
+contract LiquidityPool is Initializable, OwnableUpgradeable, UUPSUpgradeable, ReentrancyGuardTransient, PausableUntil, ILiquidityPool {
     using SafeERC20 for IERC20;
 
     //--------------------------------------------------------------------------------------
```

### src/deposits/Liquifier.sol
```diff
@@ -3,7 +3,7 @@ pragma solidity ^0.8.23;
 
 import "@openzeppelin-upgradeable/contracts/proxy/utils/UUPSUpgradeable.sol";
 import "@openzeppelin-upgradeable/contracts/access/OwnableUpgradeable.sol";
-import "@openzeppelin-upgradeable/contracts/security/ReentrancyGuardUpgradeable.sol";
+import {ReentrancyGuardTransient} from "solady/utils/ReentrancyGuardTransient.sol";
 import "@openzeppelin/contracts/token/ERC20/extensions/draft-IERC20Permit.sol";
 import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
 import "@openzeppelin/contracts/utils/math/Math.sol";
@@ -14,12 +14,13 @@ import "@etherfi/governance/interfaces/IBlacklister.sol";
 import "@etherfi/governance/utils/PausableUntil.sol";
 import "@etherfi/governance/utils/RolesLibrary.sol";
 import "@etherfi/governance/utils/DeprecatedOZPausable.sol";
+import "@etherfi/governance/utils/DeprecatedOZReentrancyGuard.sol";
 
 import "@etherfi/eigenlayer-interfaces/IStrategyManager.sol";
 import "@etherfi/eigenlayer-interfaces/IDelegationManager.sol";
 
 /// Go wild, spread eETH/weETH to the world
-contract Liquifier is Initializable, UUPSUpgradeable, OwnableUpgradeable, DeprecatedOZPausable, PausableUntil, ReentrancyGuardUpgradeable, ILiquifier {
+contract Liquifier is Initializable, UUPSUpgradeable, OwnableUpgradeable, DeprecatedOZPausable, PausableUntil, DeprecatedOZReentrancyGuard, ReentrancyGuardTransient, ILiquifier {
     using SafeERC20 for IERC20;
     using Math for uint256;
 
@@ -167,7 +168,6 @@ contract Liquifier is Initializable, UUPSUpgradeable, OwnableUpgradeable, Deprec
                         uint32 _timeBoundCapRefreshInterval) initializer external {
         __Ownable_init();
         __UUPSUpgradeable_init();
-        __ReentrancyGuard_init();
 
         timeBoundCapRefreshInterval = _timeBoundCapRefreshInterval;
     }
```

### src/governance/utils/DeprecatedOZReentrancyGuard.sol
```diff
@@ -0,0 +1,18 @@
+// SPDX-License-Identifier: MIT
+pragma solidity ^0.8.27;
+
+/**
+ * @title DeprecatedOZReentrancyGuard
+ * @notice Storage-layout placeholder that reserves the 50 storage slots formerly occupied by
+ *         OpenZeppelin's `ReentrancyGuardUpgradeable` (`uint256 _status` + `uint256[49] __gap`).
+ * @dev    Inherit this in the exact position where `ReentrancyGuardUpgradeable` used to sit, so
+ *         the storage layout of an already-deployed proxy is preserved after migrating the
+ *         reentrancy guard to Solady's transient {ReentrancyGuardTransient} (which has no
+ *         persistent storage). Declares its own gap independently — it deliberately does NOT
+ *         share a base with {DeprecatedOZPausable}, because a shared ancestor would be
+ *         deduplicated by C3 linearization and collapse two 50-slot regions into one in any
+ *         contract that inherits both. Do not add any state to this contract.
+ */
+abstract contract DeprecatedOZReentrancyGuard {
+    uint256[50] private __gap;
+}
```

### src/restaking/EtherFiRestaker.sol
```diff
@@ -3,7 +3,6 @@ pragma solidity ^0.8.23;
 
 import "@openzeppelin-upgradeable/contracts/proxy/utils/UUPSUpgradeable.sol";
 import "@openzeppelin-upgradeable/contracts/access/OwnableUpgradeable.sol";
-import "@openzeppelin-upgradeable/contracts/security/ReentrancyGuardUpgradeable.sol";
 import "@openzeppelin/contracts/token/ERC20/extensions/draft-IERC20Permit.sol";
 import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
 import "@openzeppelin/contracts/utils/math/Math.sol";
```

### src/staking/AuctionManager.sol
```diff
@@ -1,7 +1,7 @@
 // SPDX-License-Identifier: MIT
 pragma solidity ^0.8.13;
 
-import "@openzeppelin-upgradeable/contracts/security/ReentrancyGuardUpgradeable.sol";
+import {ReentrancyGuardTransient} from "solady/utils/ReentrancyGuardTransient.sol";
 import "@openzeppelin-upgradeable/contracts/access/OwnableUpgradeable.sol";
 import "@openzeppelin-upgradeable/contracts/proxy/utils/UUPSUpgradeable.sol";
 
@@ -11,14 +11,16 @@ import "@etherfi/governance/interfaces/IBlacklister.sol";
 import "@etherfi/governance/utils/PausableUntil.sol";
 import "@etherfi/governance/utils/RolesLibrary.sol";
 import "@etherfi/governance/utils/DeprecatedOZPausable.sol";
+import "@etherfi/governance/utils/DeprecatedOZReentrancyGuard.sol";
 
 contract AuctionManager is
     Initializable,
     IAuctionManager,
     DeprecatedOZPausable,
     OwnableUpgradeable,
     PausableUntil,
-    ReentrancyGuardUpgradeable,
+    DeprecatedOZReentrancyGuard,
+    ReentrancyGuardTransient,
     UUPSUpgradeable
 {
     //--------------------------------------------------------------------------------------
@@ -110,7 +112,6 @@ contract AuctionManager is
 
         __Ownable_init();
         __UUPSUpgradeable_init();
-        __ReentrancyGuard_init();
     }
 
     /// @notice Creates bid(s) for the right to run a validator node when ETH is deposited
```

### src/staking/EtherFiNodesManager.sol
```diff
@@ -4,7 +4,7 @@ pragma solidity ^0.8.24;
 import "@openzeppelin/contracts/utils/math/SafeCast.sol";
 import "@openzeppelin-upgradeable/contracts/proxy/utils/UUPSUpgradeable.sol";
 import "@openzeppelin-upgradeable/contracts/access/OwnableUpgradeable.sol";
-import "@openzeppelin-upgradeable/contracts/security/ReentrancyGuardUpgradeable.sol";
+import {ReentrancyGuardTransient} from "solady/utils/ReentrancyGuardTransient.sol";
 import "@openzeppelin/contracts/proxy/beacon/BeaconProxy.sol";
 import "@etherfi/staking/interfaces/IAuctionManager.sol";
 import "@etherfi/eigenlayer-interfaces/IEigenPod.sol";
@@ -15,14 +15,16 @@ import "@etherfi/governance/rate-limiting/interfaces/IEtherFiRateLimiter.sol";
 import "@etherfi/governance/utils/PausableUntil.sol";
 import "@etherfi/governance/utils/RolesLibrary.sol";
 import "@etherfi/governance/utils/DeprecatedOZPausable.sol";
+import "@etherfi/governance/utils/DeprecatedOZReentrancyGuard.sol";
 
 contract EtherFiNodesManager is
     Initializable,
     IEtherFiNodesManager,
     OwnableUpgradeable,
     DeprecatedOZPausable,
     PausableUntil,
-    ReentrancyGuardUpgradeable,
+    DeprecatedOZReentrancyGuard,
+    ReentrancyGuardTransient,
     UUPSUpgradeable
 {
 
```

### src/staking/StakingManager.sol
```diff
@@ -5,7 +5,6 @@ import "@openzeppelin/contracts/proxy/beacon/BeaconProxy.sol";
 import "@openzeppelin/contracts/proxy/beacon/UpgradeableBeacon.sol";
 import "@openzeppelin-upgradeable/contracts/proxy/beacon/IBeaconUpgradeable.sol";
 import "@openzeppelin-upgradeable/contracts/access/OwnableUpgradeable.sol";
-import "@openzeppelin-upgradeable/contracts/security/ReentrancyGuardUpgradeable.sol";
 import "@openzeppelin-upgradeable/contracts/proxy/utils/UUPSUpgradeable.sol";
 
 import "@etherfi/staking/interfaces/IAuctionManager.sol";
@@ -16,14 +15,15 @@ import "@etherfi/staking/interfaces/IEtherFiNodesManager.sol";
 import "@etherfi/staking/libraries/DepositDataRootGenerator.sol";
 import "@etherfi/governance/utils/RolesLibrary.sol";
 import "@etherfi/governance/utils/DeprecatedOZPausable.sol";
+import "@etherfi/governance/utils/DeprecatedOZReentrancyGuard.sol";
 
 contract StakingManager is
     Initializable,
     IStakingManager,
     IBeaconUpgradeable,
     OwnableUpgradeable,
     DeprecatedOZPausable,
-    ReentrancyGuardUpgradeable,
+    DeprecatedOZReentrancyGuard,
     UUPSUpgradeable,
     RolesLibrary
 {
```

### src/withdrawals/EtherFiRedemptionManager.sol
```diff
@@ -6,7 +6,7 @@ import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
 import "@openzeppelin/contracts/token/ERC20/extensions/draft-IERC20Permit.sol";
 import "@openzeppelin-upgradeable/contracts/token/ERC20/IERC20Upgradeable.sol";
 import "@openzeppelin-upgradeable/contracts/proxy/utils/UUPSUpgradeable.sol";
-import "@openzeppelin-upgradeable/contracts/security/ReentrancyGuardUpgradeable.sol";
+import {ReentrancyGuardTransient} from "solady/utils/ReentrancyGuardTransient.sol";
 
 import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
 import "@openzeppelin/contracts/utils/math/Math.sol";
@@ -19,6 +19,7 @@ import "@etherfi/restaking/interfaces/IEtherFiRestaker.sol";
 import "@etherfi/governance/utils/PausableUntil.sol";
 import "@etherfi/governance/utils/RolesLibrary.sol";
 import "@etherfi/governance/utils/DeprecatedOZPausable.sol";
+import "@etherfi/governance/utils/DeprecatedOZReentrancyGuard.sol";
 
 import "@etherfi/governance/rate-limiting/libraries/BucketLimiter.sol";
 
@@ -32,7 +33,7 @@ import "@etherfi/governance/interfaces/IBlacklister.sol";
     - It has a rate limiter to limit the total amount that can be redeemed in a given time period.
 */
 
-contract EtherFiRedemptionManager is Initializable, DeprecatedOZPausable, PausableUntil, ReentrancyGuardUpgradeable, UUPSUpgradeable, IEtherFiRedemptionManager {
+contract EtherFiRedemptionManager is Initializable, DeprecatedOZPausable, PausableUntil, DeprecatedOZReentrancyGuard, ReentrancyGuardTransient, UUPSUpgradeable, IEtherFiRedemptionManager {
     using SafeERC20 for IERC20;
     using Math for uint256;
 
@@ -146,7 +147,6 @@ contract EtherFiRedemptionManager is Initializable, DeprecatedOZPausable, Pausab
         if (_exitFeeInBps > BASIS_POINT_SCALE || _exitFeeSplitToTreasuryInBps > BASIS_POINT_SCALE || _lowWatermarkInBpsOfTvl > BASIS_POINT_SCALE) revert InvalidBps();
 
         __UUPSUpgradeable_init();
-        __ReentrancyGuard_init();
     }
 
     function initializeTokenParameters(address[] memory _tokens, uint16[] memory _exitFeeSplitToTreasuryInBps, uint16[] memory _exitFeeInBps, uint16[] memory _lowWatermarkInBpsOfTvl, uint256[] memory _bucketCapacity, uint256[] memory _bucketRefillRate)  external onlyAdmin {
```

### src/withdrawals/PriorityWithdrawalQueue.sol
```diff
@@ -2,7 +2,7 @@
 pragma solidity ^0.8.13;
 
 import "@openzeppelin-upgradeable/contracts/proxy/utils/UUPSUpgradeable.sol";
-import "@openzeppelin-upgradeable/contracts/security/ReentrancyGuardUpgradeable.sol";
+import {ReentrancyGuardTransient} from "solady/utils/ReentrancyGuardTransient.sol";
 import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
 import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";
 import "@openzeppelin/contracts/utils/math/Math.sol";
@@ -14,16 +14,18 @@ import "@etherfi/core/interfaces/IWeETH.sol";
 import "@etherfi/governance/interfaces/IBlacklister.sol";
 import "@etherfi/governance/utils/PausableUntil.sol";
 import "@etherfi/governance/utils/RolesLibrary.sol";
+import "@etherfi/governance/utils/DeprecatedOZReentrancyGuard.sol";
 
 /**
  * @title PriorityWithdrawalQueue
  * @notice Manages priority withdrawals for whitelisted users
  * @dev Implements priority withdrawal queue pattern
  */
 contract PriorityWithdrawalQueue is 
-    Initializable, 
-    UUPSUpgradeable, 
-    ReentrancyGuardUpgradeable,
+    Initializable,
+    UUPSUpgradeable,
+    DeprecatedOZReentrancyGuard,
+    ReentrancyGuardTransient,
     PausableUntil,
     IPriorityWithdrawalQueue
 {
@@ -149,7 +151,6 @@ contract PriorityWithdrawalQueue is
      */
     function initialize() external initializer {
         __UUPSUpgradeable_init();
-        __ReentrancyGuard_init();
 
         nonce = 1;
         shareRemainderSplitToTreasuryInBps = uint16(_BASIS_POINT_SCALE); // 100%
```

### src/withdrawals/WithdrawRequestNFT.sol
```diff
@@ -13,7 +13,7 @@ import "@etherfi/governance/interfaces/IBlacklister.sol";
 import "@openzeppelin/contracts/utils/math/Math.sol";
 import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
 import "@openzeppelin/contracts/utils/Checkpoints.sol";
-import "@etherfi/governance/utils/ReentrancyGuardNamespaced.sol";
+import {ReentrancyGuardTransient} from "solady/utils/ReentrancyGuardTransient.sol";
 import "@etherfi/governance/utils/PausableUntil.sol";
 import "@etherfi/governance/utils/RolesLibrary.sol";
 
@@ -40,7 +40,7 @@ import "@etherfi/governance/utils/RolesLibrary.sol";
  *        `ceil(amount * 1e18 / rate) <= shareOfEEth`. These keep solvency checks and
  *        the share burn within the request's own share allocation.
  */
-contract WithdrawRequestNFT is ERC721Upgradeable, UUPSUpgradeable, OwnableUpgradeable, ReentrancyGuardNamespaced, PausableUntil, IWithdrawRequestNFT {
+contract WithdrawRequestNFT is ERC721Upgradeable, UUPSUpgradeable, OwnableUpgradeable, ReentrancyGuardTransient, PausableUntil, IWithdrawRequestNFT {
     using Math for uint256;
     using SafeERC20 for IERC20;
     using Checkpoints for Checkpoints.Trace224;
```
