# [?] fix chainsecurity: fix non determinism for non sequential slashings

## Summary
Severity: Unknown
Chain: Symbiotic
Component: symbioticfi/core
Published: 2024-07-25
Source: https://github.com/symbioticfi/core/commit/e4aed315e31c194e042fbc68a25a8265798add26
Type: security-commit

## Details
fix chainsecurity: fix non determinism for non sequential slashings

## Patch
### src/contracts/slasher/BaseSlasher.sol
```diff
@@ -44,6 +44,11 @@ abstract contract BaseSlasher is Entity, StaticDelegateCallable, IBaseSlasher {
      */
     address public vault;
 
+    /**
+     * @inheritdoc IBaseSlasher
+     */
+    mapping(address network => uint48 value) public latestSlashedCaptureTimestamp;
+
     mapping(address network => mapping(address operator => Checkpoints.Trace256 amount)) internal _cumulativeSlash;
 
     modifier onlyNetworkMiddleware(address network) {
@@ -116,6 +121,12 @@ abstract contract BaseSlasher is Entity, StaticDelegateCallable, IBaseSlasher {
             );
     }
 
+    function _checkLatestSlashedCaptureTimestamp(address network, uint48 captureTimestamp) internal view {
+        if (captureTimestamp < latestSlashedCaptureTimestamp[network]) {
+            revert OutdatedCaptureTimestamp();
+        }
+    }
+
     function _checkOptIns(
         address network,
         address operator,
```

### src/contracts/slasher/Slasher.sol
```diff
@@ -48,6 +48,8 @@ contract Slasher is BaseSlasher, ISlasher {
             revert InvalidCaptureTimestamp();
         }
 
+        _checkLatestSlashedCaptureTimestamp(network, captureTimestamp);
+
         _checkOptIns(network, operator, captureTimestamp, slashHints.optInHints);
 
         slashedAmount =
@@ -56,6 +58,10 @@ contract Slasher is BaseSlasher, ISlasher {
             revert InsufficientSlash();
         }
 
+        if (latestSlashedCaptureTimestamp[network] < captureTimestamp) {
+            latestSlashedCaptureTimestamp[network] = captureTimestamp;
+        }
+
         _updateCumulativeSlash(network, operator, slashedAmount);
 
         _callOnSlash(network, operator, slashedAmount, captureTimestamp, slashHints.onSlashHints);
```

### src/contracts/slasher/VetoSlasher.sol
```diff
@@ -120,6 +120,8 @@ contract VetoSlasher is BaseSlasher, AccessControlUpgradeable, IVetoSlasher {
             revert InvalidCaptureTimestamp();
         }
 
+        _checkLatestSlashedCaptureTimestamp(network, captureTimestamp);
+
         _checkOptIns(network, operator, captureTimestamp, requestSlashHints.optInHints);
 
         amount =
@@ -169,12 +171,18 @@ contract VetoSlasher is BaseSlasher, AccessControlUpgradeable, IVetoSlasher {
             revert SlashPeriodEnded();
         }
 
+        _checkLatestSlashedCaptureTimestamp(request.network, request.captureTimestamp);
+
         if (request.completed) {
             revert SlashRequestCompleted();
         }
 
         request.completed = true;
 
+        if (latestSlashedCaptureTimestamp[request.network] < request.captureTimestamp) {
+            latestSlashedCaptureTimestamp[request.network] = request.captureTimestamp;
+        }
+
         slashedAmount = Math.min(
             request.amount,
             slashableStake(
```

### src/interfaces/slasher/IBaseSlasher.sol
```diff
@@ -4,6 +4,7 @@ pragma solidity 0.8.25;
 interface IBaseSlasher {
     error NotNetworkMiddleware();
     error NotVault();
+    error OutdatedCaptureTimestamp();
     error OperatorNotOptedInNetwork();
     error OperatorNotOptedInVault();
 
@@ -65,6 +66,13 @@ interface IBaseSlasher {
      */
     function vault() external view returns (address);
 
+    /**
+     * @notice Get a latest capture timestamp that was slashed on a network.
+     * @param network address of the network
+     * @return latest capture timestamp that was slashed
+     */
+    function latestSlashedCaptureTimestamp(address network) external view returns (uint48);
+
     /**
      * @notice Get a cumulative slash amount for an operator on a network until a given timestamp (inclusively) using a hint.
      * @param network address of the network
```

### test/slasher/Slasher.t.sol
```diff
@@ -303,6 +303,60 @@ contract SlasherTest is Test {
         );
     }
 
+    function test_SlashRevertOutdatedCaptureTimestamp(
+        uint48 epochDuration,
+        uint256 depositAmount,
+        uint256 networkLimit,
+        uint256 operatorNetworkLimit1,
+        uint256 operatorNetworkLimit2,
+        uint256 slashAmount1,
+        uint256 slashAmount2,
+        uint256 slashAmount3
+    ) public {
+        epochDuration = uint48(bound(epochDuration, 2, 10 days));
+        depositAmount = bound(depositAmount, 1, 100 * 10 ** 18);
+        networkLimit = bound(networkLimit, 1, type(uint256).max);
+        operatorNetworkLimit1 = bound(operatorNetworkLimit1, 1, type(uint256).max / 2);
+        operatorNetworkLimit2 = bound(operatorNetworkLimit2, 1, type(uint256).max / 2);
+        slashAmount1 = bound(slashAmount1, 1, type(uint256).max);
+        slashAmount2 = bound(slashAmount2, 1, type(uint256).max);
+        slashAmount3 = bound(slashAmount3, 1, type(uint256).max);
+
+        uint256 blockTimestamp = block.timestamp * block.timestamp / block.timestamp * block.timestamp / block.timestamp;
+        blockTimestamp = blockTimestamp + 1_720_700_948;
+        vm.warp(blockTimestamp);
+
+        (vault, delegator, slasher) = _getVaultAndDelegatorAndSlasher(epochDuration);
+
+        address network = alice;
+        _registerNetwork(network, alice);
+        _setMaxNetworkLimit(network, type(uint256).max);
+
+        _registerOperator(alice);
+        _registerOperator(bob);
+
+        _optInOperatorVault(alice);
+        _optInOperatorVault(bob);
+
+        _optInOperatorNetwork(alice, address(network));
+        _optInOperatorNetwork(bob, address(network));
+
+        _deposit(alice, depositAmount);
+
+        _setNetworkLimit(alice, network, networkLimit);
+
+        _setOperatorNetworkLimit(alice, network, alice, operatorNetworkLimit1);
+        _setOperatorNetworkLimit(alice, network, bob, operatorNetworkLimit2);
+
+        blockTimestamp = blockTimestamp + 2;
+        vm.warp(blockTimestamp);
+
+        _slash(alice, network, alice, slashAmount1, uint48(blockTimestamp - 1), "");
+
+        vm.expectRevert(IBaseSlasher.OutdatedCaptureTimestamp.selector);
+        _slash(alice, network, bob, slashAmount2, uint48(blockTimestamp - 2), "");
+    }
+
     function test_SlashRevertNotNetworkMiddleware(
         uint48 epochDuration,
         uint256 depositAmount,
```

### test/slasher/VetoSlasher.t.sol
```diff
@@ -710,7 +710,7 @@ contract VetoSlasherTest is Test {
         _setResolverShares(network, alice, resolverShares1, "");
     }
 
-    function test_ExecuteSlashBase(
+    function test_ExecuteSlash(
         uint48 epochDuration,
         uint48 vetoDuration,
         uint256 depositAmount,
@@ -810,6 +810,112 @@ contract VetoSlasherTest is Test {
         assertEq(slasher.cumulativeSlash(alice, alice), slashAmountReal1);
     }
 
+    function test_ExecuteSlashRevertOutdatedCaptureTimestamp1(
+        uint48 epochDuration,
+        uint48 vetoDuration,
+        uint256 depositAmount,
+        uint256 networkLimit,
+        uint256 operatorNetworkLimit1,
+        uint256 slashAmount1
+    ) public {
+        epochDuration = uint48(bound(epochDuration, 2, 10 days));
+        vetoDuration = uint48(bound(vetoDuration, 0, type(uint48).max / 2));
+        vm.assume(vetoDuration < epochDuration / 2 - 1);
+        depositAmount = bound(depositAmount, 1, 100 * 10 ** 18);
+        networkLimit = bound(networkLimit, 1, type(uint256).max);
+        operatorNetworkLimit1 = bound(operatorNetworkLimit1, 1, type(uint256).max / 2);
+        slashAmount1 = bound(slashAmount1, 1, type(uint256).max);
+
+        uint256 blockTimestamp = block.timestamp * block.timestamp / block.timestamp * block.timestamp / block.timestamp;
+        blockTimestamp = blockTimestamp + 1_720_700_948;
+        vm.warp(blockTimestamp);
+
+        (vault, delegator, slasher) = _getVaultAndDelegatorAndSlasher(epochDuration, vetoDuration);
+
+        // address network = alice;
+        _registerNetwork(alice, alice);
+        _setMaxNetworkLimit(alice, type(uint256).max);
+
+        _registerOperator(alice);
+
+        _optInOperatorVault(alice);
+
+        _optInOperatorNetwork(alice, address(alice));
+
+        _deposit(alice, depositAmount);
+
+        _setNetworkLimit(alice, alice, networkLimit);
+
+        _setOperatorNetworkLimit(alice, alice, alice, operatorNetworkLimit1);
+
+        blockTimestamp = blockTimestamp + 1;
+        vm.warp(blockTimestamp);
+
+        _requestSlash(alice, alice, alice, slashAmount1, uint48(blockTimestamp - 1), "");
+
+        blockTimestamp = blockTimestamp + vetoDuration;
+        vm.warp(blockTimestamp);
+
+        _executeSlash(alice, 0, "");
+
+        vm.expectRevert(IBaseSlasher.OutdatedCaptureTimestamp.selector);
+        _requestSlash(alice, alice, alice, slashAmount1, uint48(blockTimestamp - vetoDuration - 2), "");
+    }
+
+    function test_ExecuteSlashRevertOutdatedCaptureTimestamp2(
+        uint48 epochDuration,
+        uint48 vetoDuration,
+        uint256 depositAmount,
+        uint256 networkLimit,
+        uint256 operatorNetworkLimit1,
+        uint256 slashAmount1
+    ) public {
+        epochDuration = uint48(bound(epochDuration, 1, 10 days));
+        vetoDuration = uint48(bound(vetoDuration, 0, type(uint48).max / 2));
+        vm.assume(vetoDuration < epochDuration - 1);
+        depositAmount = bound(depositAmount, 1, 100 * 10 ** 18);
+        networkLimit = bound(networkLimit, 1, type(uint256).max);
+        operatorNetworkLimit1 = bound(operatorNetworkLimit1, 1, type(uint256).max / 2);
+        slashAmount1 = bound(slashAmount1, 1, type(uint256).max);
+
+        uint256 blockTimestamp = block.timestamp * block.timestamp / block.timestamp * block.timestamp / block.timestamp;
+        blockTimestamp = blockTimestamp + 1_720_700_948;
+        vm.warp(blockTimestamp);
+
+        (vault, delegator, slasher) = _getVaultAndDelegatorAndSlasher(epochDuration, vetoDuration);
+
+        // address network = alice;
+        _registerNetwork(alice, alice);
+        _setMaxNetworkLimit(alice, type(uint256).max);
+
+        _registerOperator(alice);
+
+        _optInOperatorVault(alice);
+
+        _optInOperatorNetwork(alice, address(alice));
+
+        _deposit(alice, depositAmount);
+
+        _setNetworkLimit(alice, alice, networkLimit);
+
+        _setOperatorNetworkLimit(alice, alice, alice, operatorNetworkLimit1);
+
+        blockTimestamp = blockTimestamp + 2;
+        vm.warp(blockTimestamp);
+
+        _requestSlash(alice, alice, alice, slashAmount1, uint48(blockTimestamp - 1), "");
+
+        _requestSlash(alice, alice, alice, slashAmount1, uint48(blockTimestamp - 2), "");
+
+        blockTimestamp = blockTimestamp + epochDuration - 2;
+        vm.warp(blockTimestamp);
+
+        _executeSlash(alice, 0, "");
+
+        vm.expectRevert(IBaseSlasher.OutdatedCaptureTimestamp.selector);
+        _executeSlash(alice, 1, "");
+    }
+
     function test_ExecuteSlashRevertSlashRequestNotExist(
         uint48 epochDuration,
         uint48 vetoDuration,
```
