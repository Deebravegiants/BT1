# [?] Merge pull request #457 from etherfi-protocol/yash/fix/deprecate-oz-reentrancy

## Summary
Severity: Unknown
Chain: EtherFi
Component: etherfi-protocol/smart-contracts
Published: 2026-06-03
Source: https://github.com/etherfi-protocol/smart-contracts/commit/bf39363c87d87ffb4f70c3cec3b249e7e4fd1f15
Type: security-commit

## Details
Merge pull request #457 from etherfi-protocol/yash/fix/deprecate-oz-reentrancy

yash/fix/deprecate-oz-pausing-reentrancy

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

### test/ReentrancyGuard.t.sol
```diff
@@ -4,13 +4,13 @@ pragma solidity ^0.8.13;
 import "@tests/TestSetup.sol";
 import "forge-std/Test.sol";
 
-import "@etherfi/governance/utils/ReentrancyGuardNamespaced.sol";
+import {ReentrancyGuardTransient} from "solady/utils/ReentrancyGuardTransient.sol";
 import "@etherfi/withdrawals/WithdrawRequestNFT.sol";
 
 /// @dev Attacker contract that owns two withdrawal NFTs. On receiving ETH during
 ///      a claimWithdraw call, it attempts to re-enter WithdrawRequestNFT via
 ///      claimWithdraw or batchClaimWithdraw using a *different* tokenId. The
-///      ReentrancyGuardNamespaced on WithdrawRequestNFT must cause the re-entry
+///      transient reentrancy guard on WithdrawRequestNFT must cause the re-entry
 ///      to revert; the try/catch lets the outer claim complete so the test can
 ///      inspect the `reentryBlocked` flag.
 contract ReentrancyAttacker {
@@ -124,9 +124,9 @@ contract ReentrancyGuardTest is TestSetup {
         assertEq(attacker.reentryAttempts(), 1, "attacker attempted re-entry");
         assertEq(attacker.reentryBlocked(), 1, "guard must block re-entry into claimWithdraw");
 
-        // Decoding the revert: must be ReentrancyGuardReentrantCall() (selector match).
+        // Decoding the revert: must be the transient guard's Reentrancy() (selector match).
         bytes4 sel = bytes4(attacker.lastRevert());
-        assertEq(sel, ReentrancyGuardNamespaced.ReentrancyGuardReentrantCall.selector, "wrong revert selector");
+        assertEq(sel, ReentrancyGuardTransient.Reentrancy.selector, "wrong revert selector");
 
         // Outer claim still completed and paid out; id2 is still claimable later.
         assertEq(address(attacker).balance, 1 ether, "outer claim paid out");
@@ -142,7 +142,7 @@ contract ReentrancyGuardTest is TestSetup {
 
         assertEq(attacker.reentryBlocked(), 1, "guard must block cross-fn re-entry via batchClaimWithdraw");
         bytes4 sel = bytes4(attacker.lastRevert());
-        assertEq(sel, ReentrancyGuardNamespaced.ReentrancyGuardReentrantCall.selector, "wrong revert selector");
+        assertEq(sel, ReentrancyGuardTransient.Reentrancy.selector, "wrong revert selector");
     }
 
     function test_batchClaimWithdraw_reentry_viaClaim_isBlocked() public {
```

### test/ReentrancyGuardStorage.t.sol
```diff
@@ -1,276 +0,0 @@
-// SPDX-License-Identifier: MIT
-pragma solidity ^0.8.13;
-
-import "@tests/TestSetup.sol";
-import "forge-std/Test.sol";
-
-import "@etherfi/governance/utils/ReentrancyGuardNamespaced.sol";
-
-/// @notice Verifies that the namespaced reentrancy guard's fixed storage slot
-///         does NOT collide with any storage used by LiquidityPool or
-///         WithdrawRequestNFT — including OZ upgradeable parents (Initializable,
-///         ContextUpgradeable, ERC721Upgradeable, OwnableUpgradeable,
-///         UUPSUpgradeable) and their `__gap` reservations.
-///
-/// Two directions of collision are tested:
-///   (1) Writes to declared state variables must not touch the guard slot.
-///   (2) Writes to the guard slot must not touch any declared state variable.
-///
-/// Mapping-slot collisions (`keccak256(abi.encode(key, mappingSlot)) == GUARD`)
-/// are cryptographically ruled out by keccak256 preimage resistance. We still
-/// exercise mapping-writing paths (ERC721 mint/transfer, `validatorSpawner`,
-/// `_requests`) and verify guard-slot integrity to catch accidental collisions
-/// with the tiny, deterministic subset of keys used in real flows.
-contract ReentrancyGuardStorageTest is TestSetup {
-    bytes32 private constant GUARD_SLOT =
-        0xcd24049d7dcc1fde21494dba8ad7a067afb6b8f14dfe804abeeec84903344e97;
-
-    // Distinctive sentinel value: not 0, not NOT_ENTERED(1), not ENTERED(2).
-    bytes32 private constant SENTINEL = bytes32(uint256(0xDEADBEEFCAFEBABE));
-
-    function setUp() public {
-        setUpTests();
-        vm.prank(admin);
-        withdrawRequestNFTInstance.unpause();
-    }
-
-    // -----------------------------------------------------------------
-    //                   Direction 1: layout is disjoint
-    // -----------------------------------------------------------------
-
-    /// @dev Sequential storage slots are tiny integers (0, 1, 2, ...). The
-    ///      guard slot is a keccak256 hash (~2^255). A uint256 cast proves the
-    ///      distance. Using a loose upper bound of 10_000 for the declared-
-    ///      storage range — both contracts use < 400 slots per `forge inspect`.
-    function test_guardSlot_outsideDeclaredSequentialRange() public {
-        uint256 guardAsUint = uint256(GUARD_SLOT);
-        assertGt(guardAsUint, 10_000, "guard slot within declared sequential storage range");
-    }
-
-    /// @dev Fresh proxy should have 0 at guard slot (uninitialized).
-    function test_guardSlot_initialValueIsZero_LP() public {
-        assertEq(vm.load(address(liquidityPoolInstance), GUARD_SLOT), bytes32(0));
-    }
-
-    function test_guardSlot_initialValueIsZero_WRN() public {
-        assertEq(vm.load(address(withdrawRequestNFTInstance), GUARD_SLOT), bytes32(0));
-    }
-
-    // -----------------------------------------------------------------
-    //     Direction 2: declared-state writes don't touch guard slot
-    // -----------------------------------------------------------------
-
-    /// @dev Plants SENTINEL at guard slot, performs many unguarded state
-    ///      mutations, verifies SENTINEL is preserved. If any declared slot
-    ///      aliased the guard slot, the sentinel would be overwritten.
-    function test_noCollision_LP_unguardedStateWrites_preserveGuardSlot() public {
-        vm.store(address(liquidityPoolInstance), GUARD_SLOT, SENTINEL);
-
-        // Unguarded setters — each touches a different declared storage slot.
-        vm.startPrank(admin);
-        liquidityPoolInstance.setFeeRecipient(address(0xBEEF));
-        liquidityPoolInstance.setValidatorSizeWei(64 ether);
-        liquidityPoolInstance.registerValidatorSpawner(address(0xABCD));
-        vm.stopPrank();
-
-        assertEq(
-            vm.load(address(liquidityPoolInstance), GUARD_SLOT),
-            SENTINEL,
-            "LP declared state writes aliased the guard slot"
-        );
-    }
-
-    /// @dev Same check via ERC721-triggering paths on WithdrawRequestNFT.
-    ///      Mints NFTs (writes to _owners, _balances, _requests mappings),
-    ///      transfers (writes to _tokenApprovals), and pause toggles.
-    function test_noCollision_WRN_mappingAndStateWrites_preserveGuardSlot() public {
-        vm.store(address(withdrawRequestNFTInstance), GUARD_SLOT, SENTINEL);
-
-        // Generate a withdraw request so the ERC721 mappings and _requests get populated.
-        vm.deal(alice, 3 ether);
-        vm.prank(alice);
-        liquidityPoolInstance.deposit{value: 3 ether}();
-        vm.startPrank(alice);
-        eETHInstance.approve(address(liquidityPoolInstance), 3 ether);
-        uint256 rid = liquidityPoolInstance.requestWithdraw(alice, 1 ether);
-        liquidityPoolInstance.requestWithdraw(alice, 1 ether);
-        liquidityPoolInstance.requestWithdraw(alice, 1 ether);
-        // ERC721 transfer path -> _tokenApprovals, _owners rewrite
-        withdrawRequestNFTInstance.approve(bob, rid);
-        withdrawRequestNFTInstance.transferFrom(alice, bob, rid);
-        vm.stopPrank();
-
-        // Admin pause toggle -> `paused` bool
-        vm.prank(admin);
-        withdrawRequestNFTInstance.pause();
-        vm.prank(admin);
-        withdrawRequestNFTInstance.unpause();
-
-        assertEq(
-            vm.load(address(withdrawRequestNFTInstance), GUARD_SLOT),
-            SENTINEL,
-            "WRN declared state writes aliased the guard slot"
-        );
-    }
-
-    // -----------------------------------------------------------------
-    //     Direction 3: guard-slot writes don't touch declared state
-    // -----------------------------------------------------------------
-
-    function test_noCollision_guardSlotWrites_doNotCorruptLPState() public {
-        // Snapshot critical declared state.
-        address feeRecipientBefore = liquidityPoolInstance.feeRecipient();
-        address stakingMgrBefore = address(liquidityPoolInstance.stakingManager());
-        address eethBefore = address(liquidityPoolInstance.eETH());
-        uint128 totalInLpBefore = liquidityPoolInstance.totalValueInLp();
-        uint128 totalOutBefore = liquidityPoolInstance.totalValueOutOfLp();
-        uint256 validatorSizeBefore = liquidityPoolInstance.validatorSizeWei();
-
-        // Fill a few exotic values into the guard slot.
-        bytes32[4] memory probes = [
-            bytes32(uint256(1)),
-            bytes32(uint256(2)),
-            bytes32(type(uint256).max),
-            SENTINEL
-        ];
-        for (uint256 i = 0; i < probes.length; i++) {
-            vm.store(address(liquidityPoolInstance), GUARD_SLOT, probes[i]);
-
-            assertEq(liquidityPoolInstance.feeRecipient(), feeRecipientBefore, "feeRecipient corrupted");
-            assertEq(address(liquidityPoolInstance.stakingManager()), stakingMgrBefore, "stakingManager corrupted");
-            assertEq(address(liquidityPoolInstance.eETH()), eethBefore, "eETH corrupted");
-            assertEq(liquidityPoolInstance.totalValueInLp(), totalInLpBefore, "totalValueInLp corrupted");
-            assertEq(liquidityPoolInstance.totalValueOutOfLp(), totalOutBefore, "totalValueOutOfLp corrupted");
-            assertEq(liquidityPoolInstance.validatorSizeWei(), validatorSizeBefore, "validatorSizeWei corrupted");
-        }
-    }
-
-    function test_noCollision_guardSlotWrites_doNotCorruptWRNState() public {
-        // Snapshot critical declared state.
-        address lpBefore = address(withdrawRequestNFTInstance.liquidityPool());
-        address eethBefore = address(withdrawRequestNFTInstance.eETH());
-        uint32 nextIdBefore = withdrawRequestNFTInstance.nextRequestId();
-        uint32 lastFinBefore = withdrawRequestNFTInstance.lastFinalizedRequestId();
-        uint16 splitBefore = withdrawRequestNFTInstance.shareRemainderSplitToTreasuryInBps();
-        bool pausedBefore = withdrawRequestNFTInstance.paused();
-
-        bytes32[4] memory probes = [
-            bytes32(uint256(1)),
-            bytes32(uint256(2)),
-            bytes32(type(uint256).max),
-            SENTINEL
-        ];
-        for (uint256 i = 0; i < probes.length; i++) {
-            vm.store(address(withdrawRequestNFTInstance), GUARD_SLOT, probes[i]);
-
-            assertEq(address(withdrawRequestNFTInstance.liquidityPool()), lpBefore, "liquidityPool corrupted");
-            assertEq(address(withdrawRequestNFTInstance.eETH()), eethBefore, "eETH corrupted");
-            assertEq(withdrawRequestNFTInstance.nextRequestId(), nextIdBefore, "nextRequestId corrupted");
-            assertEq(withdrawRequestNFTInstance.lastFinalizedRequestId(), lastFinBefore, "lastFinalizedRequestId corrupted");
-            assertEq(withdrawRequestNFTInstance.shareRemainderSplitToTreasuryInBps(), splitBefore, "split corrupted");
-            assertEq(withdrawRequestNFTInstance.paused(), pausedBefore, "paused corrupted");
-        }
-    }
-
-    // -----------------------------------------------------------------
-    //              Direction 4: guard cycles correctly
-    // -----------------------------------------------------------------
-
-    /// @dev After a guarded call completes, the slot must be NOT_ENTERED (1).
-    function test_guardSlot_setsToNotEnteredAfterCall_LP() public {
-        vm.deal(alice, 1 ether);
-        vm.prank(alice);
-        liquidityPoolInstance.deposit{value: 1 ether}();
-
-        assertEq(vm.load(address(liquidityPoolInstance), GUARD_SLOT), bytes32(uint256(1)));
-    }
-
-    function test_guardSlot_setsToNotEnteredAfterCall_WRN() public {
-        vm.deal(alice, 1 ether);
-        vm.prank(alice);
-        liquidityPoolInstance.deposit{value: 1 ether}();
-        vm.startPrank(alice);
-        eETHInstance.approve(address(liquidityPoolInstance), 1 ether);
-        uint256 rid = liquidityPoolInstance.requestWithdraw(alice, 1 ether);
-        vm.stopPrank();
-        _finalizeWithdrawalRequest(rid);
-
-        vm.prank(alice);
-        withdrawRequestNFTInstance.claimWithdraw(rid);
-
-        assertEq(vm.load(address(withdrawRequestNFTInstance), GUARD_SLOT), bytes32(uint256(1)));
-    }
-
-    /// @dev If the guard slot is pre-populated with ENTERED, the next guarded
-    ///      call must revert with the expected selector — proves we actually
-    ///      read the slot we think we do.
-    function test_guardSlot_prePopulatedENTERED_revertsAllGuardedPaths() public {
-        vm.store(address(liquidityPoolInstance), GUARD_SLOT, bytes32(uint256(2)));
-
-        vm.deal(alice, 1 ether);
-        vm.prank(alice);
-        vm.expectRevert(ReentrancyGuardNamespaced.ReentrancyGuardReentrantCall.selector);
-        liquidityPoolInstance.deposit{value: 1 ether}();
-    }
-
-    /// @dev Any non-ENTERED value in the slot must be treated as NOT_ENTERED
-    ///      (forward-compat with uninitialised 0 AND defensive against stray
-    ///      writes that aren't exactly 2). Fuzzed.
-    function testFuzz_guardSlot_nonENTERED_allowsCall(uint256 preValue) public {
-        vm.assume(preValue != 2); // ENTERED
-        vm.store(address(liquidityPoolInstance), GUARD_SLOT, bytes32(preValue));
-
-        vm.deal(alice, 1 ether);
-        vm.prank(alice);
-        liquidityPoolInstance.deposit{value: 1 ether}();
-
-        // Post-call, guard must be normalised to NOT_ENTERED (1).
-        assertEq(vm.load(address(liquidityPoolInstance), GUARD_SLOT), bytes32(uint256(1)));
-    }
-
-    // -----------------------------------------------------------------
-    //   Direction 5: mapping/ERC721 hot paths don't drift guard slot
-    // -----------------------------------------------------------------
-
-    /// @dev Heavy mapping churn: deposit many times (writes eETH share mappings
-    ///      via external contract — NB: those mappings live on eETH, not LP),
-    ///      multiple withdraw requests, pause cycles. Guard slot sentinel must
-    ///      survive across all of it (since all these paths are either
-    ///      unguarded or use the guard transiently and restore NOT_ENTERED).
-    ///
-    ///      We seed the slot with SENTINEL, then exercise ONLY unguarded state
-    ///      mutations so the guard modifier doesn't overwrite the sentinel.
-    function test_noCollision_WRN_deepMappingWrites_unguardedPaths() public {
-        vm.store(address(withdrawRequestNFTInstance), GUARD_SLOT, SENTINEL);
-
-        // Pause / unpause cycles — only modify `paused`.
-        for (uint256 i = 0; i < 3; i++) {
-            vm.prank(admin);
-            withdrawRequestNFTInstance.pause();
-            vm.prank(admin);
-            withdrawRequestNFTInstance.unpause();
-        }
-
-        assertEq(
-            vm.load(address(withdrawRequestNFTInstance), GUARD_SLOT),
-            SENTINEL,
-            "pause toggles aliased guard slot"
-        );
-    }
-
-    /// @dev Cross-contract: deposit flow touches LP.totalValueInLp / totalValueOutOfLp
-    ///      and external eETH shares mapping. Checks LP's guard slot integrity
-    ///      against mutations on OTHER contracts (must be trivially orthogonal).
-    function test_noCollision_LP_crossContractActivity() public {
-        vm.store(address(liquidityPoolInstance), GUARD_SLOT, SENTINEL);
-
-        // All of this mutates eETH (another contract), membership, admin — none of LP.
-        vm.prank(admin);
-        liquidityPoolInstance.setFeeRecipient(address(0xFEED));
-
-        assertEq(
-            vm.load(address(liquidityPoolInstance), GUARD_SLOT),
-            SENTINEL
-        );
-    }
-}
```
