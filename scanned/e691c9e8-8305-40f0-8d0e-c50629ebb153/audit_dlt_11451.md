# [?] Add reentrancy guard to VRFCoordinatorV2Mock to align its behaviour w… (#10585)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2023-09-12
Source: https://github.com/smartcontractkit/ccip/commit/5db043c994f3eecdb831e538a97a1470f1be708a
Type: security-commit

## Details
Add reentrancy guard to VRFCoordinatorV2Mock to align its behaviour w… (#10585)

* Add reentrancy guard to VRFCoordinatorV2Mock to align its behaviour with VRFCoordinatorV2

* Prettier fix

* Added nonReentrant for cancelSubscription, and removeConsumer

---------

Co-authored-by: Sri Kidambi <kidambisrinivas@users.noreply.github.com>

## Patch
### contracts/scripts/native_solc_compile_all_vrf
```diff
@@ -51,6 +51,7 @@ compileContract vrf/BatchBlockhashStore.sol
 compileContract vrf/BatchVRFCoordinatorV2.sol
 compileContract vrf/testhelpers/VRFCoordinatorV2TestHelper.sol
 compileContractAltOpts vrf/VRFCoordinatorV2.sol 10000
+compileContract mocks/VRFCoordinatorV2Mock.sol
 compileContract vrf/VRFOwner.sol
 
 # VRF V2Plus
```

### contracts/src/v0.8/mocks/VRFCoordinatorV2Mock.sol
```diff
@@ -5,8 +5,9 @@ pragma solidity ^0.8.4;
 import "../shared/interfaces/LinkTokenInterface.sol";
 import "../interfaces/VRFCoordinatorV2Interface.sol";
 import "../vrf/VRFConsumerBaseV2.sol";
+import "../shared/access/ConfirmedOwner.sol";
 
-contract VRFCoordinatorV2Mock is VRFCoordinatorV2Interface {
+contract VRFCoordinatorV2Mock is VRFCoordinatorV2Interface, ConfirmedOwner {
   uint96 public immutable BASE_FEE;
   uint96 public immutable GAS_PRICE_LINK;
   uint16 public immutable MAX_CONSUMERS = 100;
@@ -17,6 +18,7 @@ contract VRFCoordinatorV2Mock is VRFCoordinatorV2Interface {
   error TooManyConsumers();
   error InvalidConsumer();
   error InvalidRandomWords();
+  error Reentrant();
 
   event RandomWordsRequested(
     bytes32 indexed keyHash,
@@ -34,7 +36,13 @@ contract VRFCoordinatorV2Mock is VRFCoordinatorV2Interface {
   event SubscriptionCanceled(uint64 indexed subId, address to, uint256 amount);
   event ConsumerAdded(uint64 indexed subId, address consumer);
   event ConsumerRemoved(uint64 indexed subId, address consumer);
+  event ConfigSet();
 
+  struct Config {
+    // Reentrancy protection.
+    bool reentrancyLock;
+  }
+  Config private s_config;
   uint64 s_currentSubId;
   uint256 s_nextRequestId = 1;
   uint256 s_nextPreSeed = 100;
@@ -52,9 +60,18 @@ contract VRFCoordinatorV2Mock is VRFCoordinatorV2Interface {
   }
   mapping(uint256 => Request) s_requests; /* requestId */ /* request */
 
-  constructor(uint96 _baseFee, uint96 _gasPriceLink) {
+  constructor(uint96 _baseFee, uint96 _gasPriceLink) ConfirmedOwner(msg.sender) {
     BASE_FEE = _baseFee;
     GAS_PRICE_LINK = _gasPriceLink;
+    setConfig();
+  }
+
+  /**
+   * @notice Sets the configuration of the vrfv2 mock coordinator
+   */
+  function setConfig() public onlyOwner {
+    s_config = Config({reentrancyLock: false});
+    emit ConfigSet();
   }
 
   function consumerIsAdded(uint64 _subId, address _consumer) public view returns (bool) {
@@ -85,7 +102,7 @@ contract VRFCoordinatorV2Mock is VRFCoordinatorV2Interface {
    * @param _requestId the request to fulfill
    * @param _consumer the VRF randomness consumer to send the result to
    */
-  function fulfillRandomWords(uint256 _requestId, address _consumer) external {
+  function fulfillRandomWords(uint256 _requestId, address _consumer) external nonReentrant {
     fulfillRandomWordsWithOverride(_requestId, _consumer, new uint256[](0));
   }
 
@@ -114,7 +131,9 @@ contract VRFCoordinatorV2Mock is VRFCoordinatorV2Interface {
 
     VRFConsumerBaseV2 v;
     bytes memory callReq = abi.encodeWithSelector(v.rawFulfillRandomWords.selector, _requestId, _words);
+    s_config.reentrancyLock = true;
     (bool success, ) = _consumer.call{gas: req.callbackGasLimit}(callReq);
+    s_config.reentrancyLock = false;
 
     uint96 payment = uint96(BASE_FEE + ((startGas - gasleft()) * GAS_PRICE_LINK));
     if (s_subscriptions[req.subId].balance < payment) {
@@ -146,7 +165,7 @@ contract VRFCoordinatorV2Mock is VRFCoordinatorV2Interface {
     uint16 _minimumRequestConfirmations,
     uint32 _callbackGasLimit,
     uint32 _numWords
-  ) external override onlyValidConsumer(_subId, msg.sender) returns (uint256) {
+  ) external override nonReentrant onlyValidConsumer(_subId, msg.sender) returns (uint256) {
     if (s_subscriptions[_subId].owner == address(0)) {
       revert InvalidSubscription();
     }
@@ -185,7 +204,7 @@ contract VRFCoordinatorV2Mock is VRFCoordinatorV2Interface {
     return (s_subscriptions[_subId].balance, 0, s_subscriptions[_subId].owner, s_consumers[_subId]);
   }
 
-  function cancelSubscription(uint64 _subId, address _to) external override onlySubOwner(_subId) {
+  function cancelSubscription(uint64 _subId, address _to) external override onlySubOwner(_subId) nonReentrant {
     emit SubscriptionCanceled(_subId, _to, s_subscriptions[_subId].balance);
     delete (s_subscriptions[_subId]);
   }
@@ -221,7 +240,7 @@ contract VRFCoordinatorV2Mock is VRFCoordinatorV2Interface {
   function removeConsumer(
     uint64 _subId,
     address _consumer
-  ) external override onlySubOwner(_subId) onlyValidConsumer(_subId, _consumer) {
+  ) external override onlySubOwner(_subId) onlyValidConsumer(_subId, _consumer) nonReentrant {
     address[] storage consumers = s_consumers[_subId];
     for (uint256 i = 0; i < consumers.length; i++) {
       if (consumers[i] == _consumer) {
@@ -276,6 +295,13 @@ contract VRFCoordinatorV2Mock is VRFCoordinatorV2Interface {
     );
   }
 
+  modifier nonReentrant() {
+    if (s_config.reentrancyLock) {
+      revert Reentrant();
+    }
+    _;
+  }
+
   function getFallbackWeiPerUnitLink() external view returns (int256) {
     return 4000000000000000; // 0.004 Ether
   }
```

### contracts/test/v0.8/dev/VRFCoordinatorV2Mock.test.ts
```diff
@@ -262,7 +262,7 @@ describe('VRFCoordinatorV2Mock', () => {
       expect(receipt.events[0].args['success']).to.equal(true)
       assert(
         receipt.events[0].args['payment']
-          .sub(BigNumber.from('100119017000000000'))
+          .sub(BigNumber.from('100119403000000000'))
           .lt(BigNumber.from('10000000000')),
       )
 
@@ -315,7 +315,7 @@ describe('VRFCoordinatorV2Mock', () => {
       expect(receipt.events[0].args['success']).to.equal(true)
       assert(
         receipt.events[0].args['payment']
-          .sub(BigNumber.from('100119017000000000'))
+          .sub(BigNumber.from('100120516000000000'))
           .lt(BigNumber.from('10000000000')),
       )
 
```
