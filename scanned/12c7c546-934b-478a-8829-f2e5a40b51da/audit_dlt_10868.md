# [?] fix: statemind - Missing reentrancy protection on the deallocation path exposes share pricing to reentrancy from integrated protocols

## Summary
Severity: Unknown
Chain: Symbiotic
Component: symbioticfi/core
Published: 2026-06-16
Source: https://github.com/symbioticfi/core/commit/4d42fa7edb97f019b335240ac5b70f92a35ab012
Type: security-commit

## Details
fix: statemind - Missing reentrancy protection on the deallocation path exposes share pricing to reentrancy from integrated protocols

## Patch
### src/contracts/common/MigratableEntity.sol
```diff
@@ -6,11 +6,11 @@ import {IMigratableEntity} from "../../interfaces/common/IMigratableEntity.sol";
 
 import {Initializable} from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
 import {OwnableUpgradeable} from "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
-import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
+import {ReentrancyGuardTransient} from "@openzeppelin/contracts/utils/ReentrancyGuardTransient.sol";
 
 /// @title MigratableEntity
 /// @notice Base contract for controlled upgradeable entity migration lifecycle.
-abstract contract MigratableEntity is Initializable, OwnableUpgradeable, ReentrancyGuard, IMigratableEntity {
+abstract contract MigratableEntity is Initializable, OwnableUpgradeable, ReentrancyGuardTransient, IMigratableEntity {
     /// @inheritdoc IMigratableEntity
     address public immutable FACTORY;
 
```

### src/contracts/delegator/UniversalDelegator.sol
```diff
@@ -254,15 +254,15 @@ contract UniversalDelegator is
         nonReentrant
         returns (uint256 allocated)
     {
-        if (sweepPending() > 0) {
+        if (_sweepPending() > 0) {
             return 0;
         }
         return _allocate(adapter, assets);
     }
 
     /// @inheritdoc IUniversalDelegator
     function allocateAll(uint256 assets) public onlyRole(ALLOCATE_ROLE) nonReentrant returns (uint256 allocated) {
-        if (sweepPending() > 0) {
+        if (_sweepPending() > 0) {
             return 0;
         }
         return _allocateAll(assets);
@@ -275,7 +275,7 @@ contract UniversalDelegator is
         nonReentrant
         returns (uint256 allocated)
     {
-        if (sweepPending() > 0) {
+        if (_sweepPending() > 0) {
             return 0;
         }
         uint256 toDeallocate = assets.saturatingSub(VaultV2(vault).freeAssets());
@@ -296,13 +296,13 @@ contract UniversalDelegator is
             revert InvalidAdapter();
         }
         deallocated = _deallocate(adapter, assets);
-        sweepPending();
+        _sweepPending();
     }
 
     /// @inheritdoc IUniversalDelegator
     function deallocateAll(uint256 assets) public onlyRole(DEALLOCATE_ROLE) nonReentrant returns (uint256 deallocated) {
         deallocated = _deallocateAll(assets);
-        sweepPending();
+        _sweepPending();
     }
 
     /// @inheritdoc IUniversalDelegator
@@ -312,7 +312,7 @@ contract UniversalDelegator is
         nonReentrant
         returns (uint256 deallocated)
     {
-        if (sweepPending() > 0) {
+        if (_sweepPending() > 0) {
             return 0;
         }
         return _deallocateAll(assets);
@@ -344,7 +344,7 @@ contract UniversalDelegator is
             shareLimitOf[adapter]
         );
 
-        sweepPending();
+        _sweepPending();
     }
 
     /* PUBLIC FUNCTIONS (ADAPTER) */
@@ -367,15 +367,15 @@ contract UniversalDelegator is
         }
 
         // Skip allocation while pending assets remain.
-        if (sweepPending() > 0) {
+        if (_sweepPending() > 0) {
             return;
         }
 
         _allocateAll(type(uint256).max);
     }
 
     /// @inheritdoc IUniversalDelegator
-    function onWithdraw(uint256 assets) public nonReentrant {
+    function onWithdraw(uint256 assets) public {
         if (vault != msg.sender) {
             revert NotVault();
         }
@@ -386,7 +386,12 @@ contract UniversalDelegator is
     /* PUBLIC FUNCTIONS (PERMISSIONLESS) */
 
     /// @inheritdoc IUniversalDelegator
-    function sweepPending() public returns (uint256 pendingAssets) {
+    function sweepPending() public nonReentrant returns (uint256) {
+        return _sweepPending();
+    }
+
+    /// @dev Internal sweep implementation used by guarded entry points and already-guarded delegator flows.
+    function _sweepPending() public returns (uint256 pendingAssets) {
         address withdrawalQueue = VaultV2(vault).withdrawalQueue();
 
         // Try to sweep free assets as much as possible.
```

### test/adapters/AppAdapterUniversalDelegator.t.sol
```diff
@@ -25,6 +25,8 @@ import {
 import {IVaultV2, VAULT_V2_VERSION} from "../../src/interfaces/vault/IVaultV2.sol";
 import {Token} from "../mocks/Token.sol";
 
+import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
+
 contract AppAdapterUniversalMigratableEntityMock is MigratableEntity {
     constructor(address factory) MigratableEntity(factory) {}
 }
@@ -47,6 +49,73 @@ contract AppAdapterUniversalNetworkMiddlewareServiceMock {
     }
 }
 
+contract ReentrantDeallocateAdapterMock {
+    address public immutable asset;
+    address public immutable vault;
+    address public immutable attacker;
+
+    uint256 public totalAssets;
+    uint256 public sweepFreeAssets;
+    uint256 public reentrantDepositAssets;
+    uint256 public observedVaultAssetsDuringCallback;
+    uint256 public previewedReentrantShares;
+    uint256 public mintedReentrantShares;
+    bool public reentrantDepositAttempted;
+    bool public reentrantDepositSucceeded;
+    bytes public reentrantRevertData;
+
+    bool internal _deallocating;
+
+    constructor(address asset_, address vault_, address attacker_) {
+        asset = asset_;
+        vault = vault_;
+        attacker = attacker_;
+
+        IERC20(asset_).approve(vault_, type(uint256).max);
+    }
+
+    function arm(uint256 sweepFreeAssets_, uint256 reentrantDepositAssets_) external {
+        sweepFreeAssets = sweepFreeAssets_;
+        reentrantDepositAssets = reentrantDepositAssets_;
+    }
+
+    function allocatable() external pure returns (uint256) {
+        return type(uint256).max;
+    }
+
+    function freeAssets() external view returns (uint256) {
+        return _deallocating ? 0 : sweepFreeAssets;
+    }
+
+    function allocate(uint256 assets) external returns (uint256 allocated) {
+        totalAssets += assets;
+        return assets;
+    }
+
+    function deallocate(uint256 assets) external returns (uint256 deallocated) {
+        deallocated = assets < totalAssets ? assets : totalAssets;
+        totalAssets -= deallocated;
+        sweepFreeAssets = sweepFreeAssets > deallocated ? sweepFreeAssets - deallocated : 0;
+
+        observedVaultAssetsDuringCallback = VaultV2(vault).totalAssets();
+        previewedReentrantShares = VaultV2(vault).previewDeposit(reentrantDepositAssets);
+
+        if (!reentrantDepositAttempted && reentrantDepositAssets > 0) {
+            reentrantDepositAttempted = true;
+            _deallocating = true;
+            try VaultV2(vault).deposit(reentrantDepositAssets, attacker) returns (uint256 shares) {
+                reentrantDepositSucceeded = true;
+                mintedReentrantShares = shares;
+            } catch (bytes memory data) {
+                reentrantRevertData = data;
+            }
+            _deallocating = false;
+        }
+    }
+
+    function requestDeallocate(uint256) external {}
+}
+
 contract AppAdapterUniversalDelegatorTest is Test {
     using Subnetwork for address;
 
@@ -590,6 +659,88 @@ contract AppAdapterUniversalDelegatorTest is Test {
         assertEq(assetToken.balanceOf(address(this)), receiverBalanceBefore + expectedAssets);
     }
 
+    function test_DepositSweepsPendingQueueWithVaultFreeAssets() public {
+        WithdrawalQueue queue = _preparePendingQueueWithYield();
+        uint256 pendingSharesBefore = queue.pendingShares();
+        uint256 queueBalanceBefore = assetToken.balanceOf(address(queue));
+        uint256 assets = 50;
+
+        assetToken.approve(address(vault), assets);
+        uint256 mintedShares = vault.deposit(assets, address(this));
+
+        assertGt(mintedShares, 0);
+        _assertPendingQueueFilled(queue, pendingSharesBefore, queueBalanceBefore);
+    }
+
+    function test_MintSweepsPendingQueueWithVaultFreeAssets() public {
+        WithdrawalQueue queue = _preparePendingQueueWithYield();
+        uint256 pendingSharesBefore = queue.pendingShares();
+        uint256 queueBalanceBefore = assetToken.balanceOf(address(queue));
+        uint256 shares = 10;
+        uint256 expectedAssets = vault.previewMint(shares);
+
+        assetToken.approve(address(vault), expectedAssets);
+        uint256 assets = vault.mint(shares, address(this));
+
+        assertEq(assets, expectedAssets);
+        _assertPendingQueueFilled(queue, pendingSharesBefore, queueBalanceBefore);
+    }
+
+    function test_SweepPendingFillsQueueWithVaultFreeAssets() public {
+        WithdrawalQueue queue = _preparePendingQueueWithYield();
+        uint256 pendingSharesBefore = queue.pendingShares();
+        uint256 queueBalanceBefore = assetToken.balanceOf(address(queue));
+
+        uint256 pendingAssets = delegator.sweepPending();
+
+        assertEq(pendingAssets, 0);
+        _assertPendingQueueFilled(queue, pendingSharesBefore, queueBalanceBefore);
+    }
+
+    function test_DirectFillFillsQueueWithVaultFreeAssets() public {
+        WithdrawalQueue queue = _preparePendingQueueWithYield();
+        uint256 pendingSharesBefore = queue.pendingShares();
+        uint256 queueBalanceBefore = assetToken.balanceOf(address(queue));
+
+        (uint256 assetsFilled, uint256 sharesFilled) = queue.fill();
+
+        assertGt(assetsFilled, 0);
+        assertEq(sharesFilled, pendingSharesBefore);
+        _assertPendingQueueFilled(queue, pendingSharesBefore, queueBalanceBefore);
+    }
+
+    function test_SweepPendingBlocksReentrantDepositDuringAdapterDeallocation() public {
+        address attacker = makeAddr("attacker");
+        VaultV2 targetVault = _createVault();
+        UniversalDelegator targetDelegator = _createDelegator(targetVault);
+        targetVault.setDelegator(address(targetDelegator));
+
+        assetToken.approve(address(targetVault), 100);
+        targetVault.deposit(100, address(this));
+
+        ReentrantDeallocateAdapterMock reentrantAdapter =
+            new ReentrantDeallocateAdapterMock(address(assetToken), address(targetVault), attacker);
+        adapterRegistry.setWhitelistedStatus(address(targetVault), address(reentrantAdapter), true);
+        targetDelegator.addAdapter(address(reentrantAdapter));
+        targetDelegator.setLimits(address(reentrantAdapter), type(uint256).max, MAX_SHARE);
+        targetDelegator.allocate(address(reentrantAdapter), 100);
+
+        uint256 reentrantDepositAssets = 100;
+        uint256 deallocatedAssets = 50;
+        assetToken.transfer(address(reentrantAdapter), reentrantDepositAssets);
+        reentrantAdapter.arm(deallocatedAssets, reentrantDepositAssets);
+
+        uint256 pendingAssets = targetDelegator.sweepPending();
+
+        assertEq(pendingAssets, 0);
+        assertTrue(reentrantAdapter.reentrantDepositAttempted());
+        assertFalse(reentrantAdapter.reentrantDepositSucceeded());
+        assertEq(targetVault.balanceOf(attacker), 0);
+        assertEq(reentrantAdapter.observedVaultAssetsDuringCallback(), 50);
+        assertGt(reentrantAdapter.previewedReentrantShares(), reentrantDepositAssets);
+        assertEq(_revertSelector(reentrantAdapter.reentrantRevertData()), _reentrancyGuardRevertSelector());
+    }
+
     function _requestAllocatedWithdrawal(uint256 assets)
         internal
         returns (WithdrawalQueue queue, uint256 tokenId, uint256 shares)
@@ -657,6 +808,28 @@ contract AppAdapterUniversalDelegatorTest is Test {
         assertTrue(vm.revertToState(snapshotId));
     }
 
+    function _assertPendingQueueFilled(WithdrawalQueue queue, uint256 pendingSharesBefore, uint256 queueBalanceBefore)
+        internal
+        view
+    {
+        assertEq(queue.pendingShares(), 0);
+        assertEq(queue.totalFilled(), pendingSharesBefore);
+        assertGt(assetToken.balanceOf(address(queue)), queueBalanceBefore);
+    }
+
+    function _revertSelector(bytes memory data) internal pure returns (bytes4 selector) {
+        if (data.length < 4) {
+            return bytes4(0);
+        }
+        assembly {
+            selector := mload(add(data, 0x20))
+        }
+    }
+
+    function _reentrancyGuardRevertSelector() internal pure returns (bytes4) {
+        return bytes4(keccak256("ReentrancyGuardReentrantCall()"));
+    }
+
     function _createVault() internal returns (VaultV2) {
         bytes memory data = abi.encode(
             IVaultV2.InitParams({
```

### test/invariant/PendingWithdrawalQueueInvariants.t.sol
```diff
@@ -33,11 +33,21 @@ contract PendingWithdrawalQueueInvariantsTest is Test {
         targetContract(address(handler));
     }
 
+    function test_DepositWhilePendingDoesNotRevert() public {
+        handler.depositWhilePending(1);
+
+        assertEq(handler.unexpectedActionRevertSelector(), bytes4(0));
+    }
+
     function invariant_NoAllocationWhileWithdrawalQueueHasPendingAssets() public view {
         assertEq(handler.allocatedWhilePending(), 0);
     }
 
     function invariant_NoInstantWithdrawalWhileWithdrawalQueueHasPendingAssets() public view {
         assertEq(handler.withdrawnWhilePending(), 0);
     }
+
+    function invariant_PendingQueueMaintenanceActionsDoNotRevert() public view {
+        assertEq(handler.unexpectedActionRevertSelector(), bytes4(0));
+    }
 }
```

### test/invariant/handlers/PendingWithdrawalQueueHandler.sol
```diff
@@ -74,6 +74,7 @@ contract PendingWithdrawalQueueHandler is Test {
 
     uint256 public allocatedWhilePending;
     uint256 public withdrawnWhilePending;
+    bytes4 public unexpectedActionRevertSelector;
 
     VaultFactory internal vaultFactory;
     DelegatorFactory internal delegatorFactory;
@@ -104,7 +105,10 @@ contract PendingWithdrawalQueueHandler is Test {
         deal(address(collateral), DEPOSITOR, amount);
         vm.startPrank(DEPOSITOR);
         collateral.approve(address(vault), amount);
-        vault.deposit(amount, DEPOSITOR);
+        try vault.deposit(amount, DEPOSITOR) {}
+        catch {
+            _recordUnexpectedActionRevert(this.depositWhilePending.selector);
+        }
         vm.stopPrank();
 
         _accountAllocationIfStillPending(adapterAssetsBefore);
@@ -123,7 +127,10 @@ contract PendingWithdrawalQueueHandler is Test {
         deal(address(collateral), DEPOSITOR, assets);
         vm.startPrank(DEPOSITOR);
         collateral.approve(address(vault), assets);
-        try vault.mint(shares, DEPOSITOR) {} catch {}
+        try vault.mint(shares, DEPOSITOR) {}
+        catch {
+            _recordUnexpectedActionRevert(this.mintWhilePending.selector);
+        }
         vm.stopPrank();
 
         _accountAllocationIfStillPending(adapterAssetsBefore);
@@ -139,7 +146,12 @@ contract PendingWithdrawalQueueHandler is Test {
         uint256 amount = _pendingBound(amountSeed, pendingBefore);
         _addVaultFreeAssets(amount);
 
-        uint256 allocated = delegator.allocate(address(adapter), amount);
+        uint256 allocated;
+        try delegator.allocate(address(adapter), amount) returns (uint256 allocated_) {
+            allocated = allocated_;
+        } catch {
+            _recordUnexpectedActionRevert(this.allocateWhilePending.selector);
+        }
         if (queue.pendingAssets() > 0) {
             allocatedWhilePending += allocated;
         }
@@ -156,7 +168,12 @@ contract PendingWithdrawalQueueHandler is Test {
         uint256 amount = _pendingBound(amountSeed, pendingBefore);
         _addVaultFreeAssets(amount);
 
-        uint256 allocated = delegator.allocateAll(type(uint256).max);
+        uint256 allocated;
+        try delegator.allocateAll(type(uint256).max) returns (uint256 allocated_) {
+            allocated = allocated_;
+        } catch {
+            _recordUnexpectedActionRevert(this.allocateAllWhilePending.selector);
+        }
         if (queue.pendingAssets() > 0) {
             allocatedWhilePending += allocated;
         }
@@ -220,7 +237,10 @@ contract PendingWithdrawalQueueHandler is Test {
         uint256 shares = bound(sharesSeed, 1, balance);
         vm.startPrank(BOB);
         vault.approve(address(queue), shares);
-        try queue.requestRedeem(shares, BOB) {} catch {}
+        try queue.requestRedeem(shares, BOB) {}
+        catch {
+            _recordUnexpectedActionRevert(this.requestRedeemWhilePending.selector);
+        }
         vm.stopPrank();
     }
 
@@ -231,7 +251,10 @@ contract PendingWithdrawalQueueHandler is Test {
         }
 
         _addVaultFreeAssets(_pendingBound(freeAssetsSeed, pendingBefore));
-        try queue.fill() {} catch {}
+        try queue.fill() {}
+        catch {
+            _recordUnexpectedActionRevert(this.fillQueueWhilePending.selector);
+        }
     }
 
     function claimQueueWhilePending() external {
@@ -241,7 +264,10 @@ contract PendingWithdrawalQueueHandler is Test {
 
         try queue.ownerOf(0) returns (address owner) {
             vm.prank(owner);
-            try queue.claim(0, owner) {} catch {}
+            try queue.claim(0, owner) {}
+            catch {
+                _recordUnexpectedActionRevert(this.claimQueueWhilePending.selector);
+            }
         } catch {}
     }
 
@@ -250,7 +276,10 @@ contract PendingWithdrawalQueueHandler is Test {
             return;
         }
 
-        try delegator.sweepPending() {} catch {}
+        try delegator.sweepPending() {}
+        catch {
+            _recordUnexpectedActionRevert(this.sweepPendingWhilePending.selector);
+        }
     }
 
     function setLimitsWhilePending(uint256 assetsSeed, uint256 shareSeed) external {
@@ -260,7 +289,10 @@ contract PendingWithdrawalQueueHandler is Test {
 
         uint256 assets = bound(assetsSeed, 0, adapter.totalAssets() + MAX_ACTION_AMOUNT);
         uint256 share = bound(shareSeed, 0, MAX_SHARE);
-        try delegator.setLimits(address(adapter), assets, share) {} catch {}
+        try delegator.setLimits(address(adapter), assets, share) {}
+        catch {
+            _recordUnexpectedActionRevert(this.setLimitsWhilePending.selector);
+        }
     }
 
     function setAutoAllocateWhilePending(uint256 enabledSeed) external {
@@ -272,7 +304,10 @@ contract PendingWithdrawalQueueHandler is Test {
         if (adapters.length != 0) {
             adapters[0] = address(adapter);
         }
-        try delegator.setAutoAllocateAdapters(adapters) {} catch {}
+        try delegator.setAutoAllocateAdapters(adapters) {}
+        catch {
+            _recordUnexpectedActionRevert(this.setAutoAllocateWhilePending.selector);
+        }
     }
 
     function redeemWhilePending(uint256 sharesSeed, uint256 freeAssetsSeed) external {
@@ -477,4 +512,10 @@ contract PendingWithdrawalQueueHandler is Test {
             withdrawnWhilePending += collateral.balanceOf(BOB) - bobBalanceBefore;
         }
     }
+
+    function _recordUnexpectedActionRevert(bytes4 selector) internal {
+        if (unexpectedActionRevertSelector == bytes4(0)) {
+            unexpectedActionRevertSelector = selector;
+        }
+    }
 }
```
