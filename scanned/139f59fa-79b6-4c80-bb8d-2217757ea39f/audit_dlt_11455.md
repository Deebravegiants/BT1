# [?] fix: fold reentrancy check into s_config (#10142)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2023-08-10
Source: https://github.com/smartcontractkit/ccip/commit/e09a969d86ec39aafd2db796ba691de205ca50bc
Type: security-commit

## Details
fix: fold reentrancy check into s_config (#10142)

* fix: fold reentrancy check into s_config

* chore: revert gas profiling changes

* fix: native_solc_compile_all_vrf

* fix: remove unused updateConsumerNonce function

* fix: remove script changes

## Patch
### contracts/scripts/native_solc_compile_all_vrf
```diff
@@ -82,5 +82,3 @@ compileContract vrf/testhelpers/VRFLoadTestOwnerlessConsumer.sol
 compileContract vrf/testhelpers/VRFLoadTestExternalSubOwner.sol
 compileContract vrf/testhelpers/VRFV2LoadTestWithMetrics.sol
 compileContract vrf/testhelpers/VRFV2OwnerTestConsumer.sol
-
-
```

### contracts/src/v0.8/dev/vrf/SubscriptionAPI.sol
```diff
@@ -4,11 +4,10 @@ pragma solidity ^0.8.0;
 import "../../shared/interfaces/LinkTokenInterface.sol";
 import "../../shared/access/ConfirmedOwner.sol";
 import "../../interfaces/AggregatorV3Interface.sol";
-import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
 import "../../shared/interfaces/IERC677Receiver.sol";
 import "../interfaces/IVRFSubscriptionV2Plus.sol";
 
-abstract contract SubscriptionAPI is ConfirmedOwner, ReentrancyGuard, IERC677Receiver, IVRFSubscriptionV2Plus {
+abstract contract SubscriptionAPI is ConfirmedOwner, IERC677Receiver, IVRFSubscriptionV2Plus {
   /// @dev may not be provided upon construction on some chains due to lack of availability
   LinkTokenInterface public LINK;
   /// @dev may not be provided upon construction on some chains due to lack of availability
@@ -83,6 +82,36 @@ abstract contract SubscriptionAPI is ConfirmedOwner, ReentrancyGuard, IERC677Rec
   event SubscriptionOwnerTransferRequested(uint256 indexed subId, address from, address to);
   event SubscriptionOwnerTransferred(uint256 indexed subId, address from, address to);
 
+  struct Config {
+    uint16 minimumRequestConfirmations;
+    uint32 maxGasLimit;
+    // Reentrancy protection.
+    bool reentrancyLock;
+    // stalenessSeconds is how long before we consider the feed price to be stale
+    // and fallback to fallbackWeiPerUnitLink.
+    uint32 stalenessSeconds;
+    // Gas to cover oracle payment after we calculate the payment.
+    // We make it configurable in case those operations are repriced.
+    // The recommended number is below, though it may vary slightly
+    // if certain chains do not implement certain EIP's.
+    // 21000 + // base cost of the transaction
+    // 100 + 5000 + // warm subscription balance read and update. See https://eips.ethereum.org/EIPS/eip-2929
+    // 2*2100 + 5000 - // cold read oracle address and oracle balance and first time oracle balance update, note first time will be 20k, but 5k subsequently
+    // 4800 + // request delete refund (refunds happen after execution), note pre-london fork was 15k. See https://eips.ethereum.org/EIPS/eip-3529
+    // 6685 + // Positive static costs of argument encoding etc. note that it varies by +/- x*12 for every x bytes of non-zero data in the proof.
+    // Total: 37,185 gas.
+    uint32 gasAfterPaymentCalculation;
+  }
+  Config public s_config;
+
+  error Reentrant();
+  modifier nonReentrant() {
+    if (s_config.reentrancyLock) {
+      revert Reentrant();
+    }
+    _;
+  }
+
   constructor() ConfirmedOwner(msg.sender) {}
 
   /**
```

### contracts/src/v0.8/dev/vrf/VRFCoordinatorV2Plus.sol
```diff
@@ -67,26 +67,8 @@ contract VRFCoordinatorV2Plus is VRF, SubscriptionAPI {
     bool success
   );
 
-  struct Config {
-    uint16 minimumRequestConfirmations;
-    uint32 maxGasLimit;
-    // stalenessSeconds is how long before we consider the feed price to be stale
-    // and fallback to fallbackWeiPerUnitLink.
-    uint32 stalenessSeconds;
-    // Gas to cover oracle payment after we calculate the payment.
-    // We make it configurable in case those operations are repriced.
-    // The recommended number is below, though it may vary slightly
-    // if certain chains do not implement certain EIP's.
-    // 21000 + // base cost of the transaction
-    // 100 + 5000 + // warm subscription balance read and update. See https://eips.ethereum.org/EIPS/eip-2929
-    // 2*2100 + 5000 - // cold read oracle address and oracle balance and first time oracle balance update, note first time will be 20k, but 5k subsequently
-    // 4800 + // request delete refund (refunds happen after execution), note pre-london fork was 15k. See https://eips.ethereum.org/EIPS/eip-3529
-    // 6685 + // Positive static costs of argument encoding etc. note that it varies by +/- x*12 for every x bytes of non-zero data in the proof.
-    // Total: 37,185 gas.
-    uint32 gasAfterPaymentCalculation;
-  }
   int256 public s_fallbackWeiPerUnitLink;
-  Config public s_config;
+
   FeeConfig public s_feeConfig;
   struct FeeConfig {
     // Flat fee charged per fulfillment in millionths of link
@@ -185,7 +167,8 @@ contract VRFCoordinatorV2Plus is VRF, SubscriptionAPI {
       minimumRequestConfirmations: minimumRequestConfirmations,
       maxGasLimit: maxGasLimit,
       stalenessSeconds: stalenessSeconds,
-      gasAfterPaymentCalculation: gasAfterPaymentCalculation
+      gasAfterPaymentCalculation: gasAfterPaymentCalculation,
+      reentrancyLock: false
     });
     s_feeConfig = feeConfig;
     s_fallbackWeiPerUnitLink = fallbackWeiPerUnitLink;
@@ -427,7 +410,9 @@ contract VRFCoordinatorV2Plus is VRF, SubscriptionAPI {
     // during the consumers callback code via reentrancyLock.
     // Note that callWithExactGas will revert if we do not have sufficient gas
     // to give the callee their requested amount.
+    s_config.reentrancyLock = true;
     bool success = callWithExactGas(rc.callbackGasLimit, rc.sender, resp);
+    s_config.reentrancyLock = false;
 
     // Increment the req count for the subscription.
     uint64 reqCount = s_subscriptions[rc.subId].reqCount;
```

### core/gethwrappers/generation/generated-wrapper-dependency-versions-do-not-edit.txt
```diff
@@ -74,7 +74,7 @@ vrf_consumer_v2_upgradeable_example: ../../contracts/solc/v0.8.6/VRFConsumerV2Up
 vrf_coordinator_mock: ../../contracts/solc/v0.8.6/VRFCoordinatorMock.abi ../../contracts/solc/v0.8.6/VRFCoordinatorMock.bin 5c495cf8df1f46d8736b9150cdf174cce358cb8352f60f0d5bb9581e23920501
 vrf_coordinator_v2: ../../contracts/solc/v0.8.6/VRFCoordinatorV2.abi ../../contracts/solc/v0.8.6/VRFCoordinatorV2.bin 75c87cf1624a401ac6303df9c8e04896aa8a53849e8b0c3d7340a9d089ef6d4b
 vrf_coordinator_v2_plus_v2_example: ../../contracts/solc/v0.8.6/VRFCoordinatorV2Plus_V2Example.abi ../../contracts/solc/v0.8.6/VRFCoordinatorV2Plus_V2Example.bin 02d0ec25e4f3d72f818e7ebc2b5f5949a94889ab0da091f0d3e7f5e4a20a0bb6
-vrf_coordinator_v2plus: ../../contracts/solc/v0.8.6/VRFCoordinatorV2Plus.abi ../../contracts/solc/v0.8.6/VRFCoordinatorV2Plus.bin 109aa4e3d3ca95738d8da15aefc2bf8b09b8f90204ef1a1176ca2d0a8ffe9a9a
+vrf_coordinator_v2plus: ../../contracts/solc/v0.8.6/VRFCoordinatorV2Plus.abi ../../contracts/solc/v0.8.6/VRFCoordinatorV2Plus.bin c7714a63e793d5795f8c787de3a0cddeff240df8458fc8f89c96b2480ae09823
 vrf_external_sub_owner_example: ../../contracts/solc/v0.8.6/VRFExternalSubOwnerExample.abi ../../contracts/solc/v0.8.6/VRFExternalSubOwnerExample.bin 14f888eb313930b50233a6f01ea31eba0206b7f41a41f6311670da8bb8a26963
 vrf_load_test_external_sub_owner: ../../contracts/solc/v0.8.6/VRFLoadTestExternalSubOwner.abi ../../contracts/solc/v0.8.6/VRFLoadTestExternalSubOwner.bin 2097faa70265e420036cc8a3efb1f1e0836ad2d7323b295b9a26a125dbbe6c7d
 vrf_load_test_ownerless_consumer: ../../contracts/solc/v0.8.6/VRFLoadTestOwnerlessConsumer.abi ../../contracts/solc/v0.8.6/VRFLoadTestOwnerlessConsumer.bin 74f914843cbc70b9c3079c3e1c709382ce415225e8bb40113e7ac018bfcb0f5c
```
