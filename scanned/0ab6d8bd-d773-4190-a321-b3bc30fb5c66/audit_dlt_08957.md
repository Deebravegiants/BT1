# [?] improve: Public functions making external contract calls should guard against reentrancy (#62)

## Summary
Severity: Unknown
Chain: Across
Component: across-protocol/contracts
Published: 2022-03-02
Source: https://github.com/across-protocol/contracts/commit/7c79fe34a7387a009f3a21096cb1513e0468cade
Type: security-commit

## Details
improve: Public functions making external contract calls should guard against reentrancy (#62)

* improve: Add reentrancy guards only to methods that make external calls

* remove from adapters

## Patch
### contracts/Arbitrum_SpokePool.sol
```diff
@@ -59,7 +59,7 @@ contract Arbitrum_SpokePool is SpokePool {
      * @notice Change L2 gateway router. Callable only by admin.
      * @param newL2GatewayRouter New L2 gateway router.
      */
-    function setL2GatewayRouter(address newL2GatewayRouter) public onlyAdmin nonReentrant {
+    function setL2GatewayRouter(address newL2GatewayRouter) public onlyAdmin {
         _setL2GatewayRouter(newL2GatewayRouter);
     }
 
@@ -68,7 +68,7 @@ contract Arbitrum_SpokePool is SpokePool {
      * @param l2Token Arbitrum token.
      * @param l1Token Ethereum version of l2Token.
      */
-    function whitelistToken(address l2Token, address l1Token) public onlyAdmin nonReentrant {
+    function whitelistToken(address l2Token, address l1Token) public onlyAdmin {
         _whitelistToken(l2Token, l1Token);
     }
 
```

### contracts/HubPool.sol
```diff
@@ -267,7 +267,13 @@ contract HubPool is HubPoolInterface, Testable, Lockable, MultiCaller, Ownable {
      * @param newBondToken New bond currency.
      * @param newBondAmount New bond amount.
      */
-    function setBond(IERC20 newBondToken, uint256 newBondAmount) public override onlyOwner noActiveRequests {
+    function setBond(IERC20 newBondToken, uint256 newBondAmount)
+        public
+        override
+        onlyOwner
+        noActiveRequests
+        nonReentrant
+    {
         // Check that this token is on the whitelist.
         AddressWhitelistInterface addressWhitelist = AddressWhitelistInterface(
             finder.getImplementationAddress(OracleInterfaces.CollateralWhitelist)
@@ -294,7 +300,7 @@ contract HubPool is HubPoolInterface, Testable, Lockable, MultiCaller, Ownable {
      * @notice Sets identifier for root bundle disputes.. Callable only by owner.
      * @param newIdentifier New identifier.
      */
-    function setIdentifier(bytes32 newIdentifier) public override onlyOwner noActiveRequests {
+    function setIdentifier(bytes32 newIdentifier) public override onlyOwner noActiveRequests nonReentrant {
         IdentifierWhitelistInterface identifierWhitelist = IdentifierWhitelistInterface(
             finder.getImplementationAddress(OracleInterfaces.IdentifierWhitelist)
         );
@@ -331,7 +337,7 @@ contract HubPool is HubPoolInterface, Testable, Lockable, MultiCaller, Ownable {
         uint256 destinationChainId,
         address originToken,
         address destinationToken
-    ) public override onlyOwner {
+    ) public override onlyOwner nonReentrant {
         whitelistedRoutes[_whitelistedRouteKey(originChainId, originToken, destinationChainId)] = destinationToken;
 
         // Whitelist the same route on the origin network.
@@ -347,7 +353,7 @@ contract HubPool is HubPoolInterface, Testable, Lockable, MultiCaller, Ownable {
      * Callable only by owner.
      * @param l1Token Token to provide liquidity for.
      */
-    function enableL1TokenForLiquidityProvision(address l1Token) public override onlyOwner {
+    function enableL1TokenForLiquidityProvision(address l1Token) public override onlyOwner nonReentrant {
         if (pooledTokens[l1Token].lpToken == address(0))
             pooledTokens[l1Token].lpToken = lpTokenFactory.createLpToken(l1Token);
 
@@ -381,7 +387,7 @@ contract HubPool is HubPoolInterface, Testable, Lockable, MultiCaller, Ownable {
      * @param l1Token Token to deposit into this contract.
      * @param l1TokenAmount Amount of liquidity to provide.
      */
-    function addLiquidity(address l1Token, uint256 l1TokenAmount) public payable override {
+    function addLiquidity(address l1Token, uint256 l1TokenAmount) public payable override nonReentrant {
         require(pooledTokens[l1Token].isEnabled, "Token not enabled");
         // If this is the weth pool and the caller sends msg.value then the msg.value must match the l1TokenAmount.
         // Else, msg.value must be set to 0.
```

### contracts/Lockable.sol
```diff
@@ -5,6 +5,9 @@ pragma solidity ^0.8.0;
  * @title A contract that provides modifiers to prevent reentrancy to state-changing and view-only methods. This contract
  * is inspired by https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/ReentrancyGuard.sol
  * and https://github.com/balancer-labs/balancer-core/blob/master/contracts/BPool.sol.
+ * @dev The reason why we use this local contract instead of importing from uma/contracts is because of the addition
+ * of the internal method `functionCallStackOriginatesFromOutsideThisContract` which doesn't exist in the one exported
+ * by uma/contracts.
  */
 contract Lockable {
     bool internal _notEntered;
```

### contracts/Polygon_SpokePool.sol
```diff
@@ -85,7 +85,7 @@ contract Polygon_SpokePool is IFxMessageProcessor, SpokePool {
      * @notice Change FxChild address. Callable only by admin via processMessageFromRoot.
      * @param newFxChild New FxChild.
      */
-    function setFxChild(address newFxChild) public onlyAdmin nonReentrant {
+    function setFxChild(address newFxChild) public onlyAdmin {
         fxChild = newFxChild;
         emit SetFxChild(fxChild);
     }
@@ -94,7 +94,7 @@ contract Polygon_SpokePool is IFxMessageProcessor, SpokePool {
      * @notice Change polygonTokenBridger address. Callable only by admin via processMessageFromRoot.
      * @param newPolygonTokenBridger New Polygon Token Bridger contract.
      */
-    function setPolygonTokenBridger(address payable newPolygonTokenBridger) public onlyAdmin nonReentrant {
+    function setPolygonTokenBridger(address payable newPolygonTokenBridger) public onlyAdmin {
         polygonTokenBridger = PolygonTokenBridger(newPolygonTokenBridger);
         emit SetPolygonTokenBridger(address(polygonTokenBridger));
     }
@@ -113,7 +113,7 @@ contract Polygon_SpokePool is IFxMessageProcessor, SpokePool {
         uint256, /*stateId*/
         address rootMessageSender,
         bytes calldata data
-    ) public validateInternalCalls {
+    ) public validateInternalCalls nonReentrant {
         // Validation logic.
         require(msg.sender == fxChild, "Not from fxChild");
         require(rootMessageSender == crossDomainAdmin, "Not from mainnet admin");
```

### contracts/SpokePool.sol
```diff
@@ -191,15 +191,15 @@ abstract contract SpokePool is SpokePoolInterface, Testable, Lockable, MultiCall
      * @notice Change cross domain admin address. Callable by admin only.
      * @param newCrossDomainAdmin New cross domain admin.
      */
-    function setCrossDomainAdmin(address newCrossDomainAdmin) public override onlyAdmin nonReentrant {
+    function setCrossDomainAdmin(address newCrossDomainAdmin) public override onlyAdmin {
         _setCrossDomainAdmin(newCrossDomainAdmin);
     }
 
     /**
      * @notice Change L1 hub pool address. Callable by admin only.
      * @param newHubPool New hub pool.
      */
-    function setHubPool(address newHubPool) public override onlyAdmin nonReentrant {
+    function setHubPool(address newHubPool) public override onlyAdmin {
         _setHubPool(newHubPool);
     }
 
@@ -213,7 +213,7 @@ abstract contract SpokePool is SpokePoolInterface, Testable, Lockable, MultiCall
         address originToken,
         uint256 destinationChainId,
         bool enabled
-    ) public override onlyAdmin nonReentrant {
+    ) public override onlyAdmin {
         enabledDepositRoutes[originToken][destinationChainId] = enabled;
         emit EnabledDepositRoute(originToken, destinationChainId, enabled);
     }
@@ -222,7 +222,7 @@ abstract contract SpokePool is SpokePoolInterface, Testable, Lockable, MultiCall
      * @notice Change allowance for deposit quote time to differ from current block time. Callable by admin only.
      * @param newDepositQuoteTimeBuffer New quote time buffer.
      */
-    function setDepositQuoteTimeBuffer(uint32 newDepositQuoteTimeBuffer) public override onlyAdmin nonReentrant {
+    function setDepositQuoteTimeBuffer(uint32 newDepositQuoteTimeBuffer) public override onlyAdmin {
         depositQuoteTimeBuffer = newDepositQuoteTimeBuffer;
         emit SetDepositQuoteTimeBuffer(newDepositQuoteTimeBuffer);
     }
@@ -236,7 +236,7 @@ abstract contract SpokePool is SpokePoolInterface, Testable, Lockable, MultiCall
      * @param slowRelayRoot Merkle root containing slow relay fulfillment leaves that can be individually executed via
      * executeSlowRelayRoot().
      */
-    function relayRootBundle(bytes32 relayerRefundRoot, bytes32 slowRelayRoot) public override onlyAdmin nonReentrant {
+    function relayRootBundle(bytes32 relayerRefundRoot, bytes32 slowRelayRoot) public override onlyAdmin {
         uint32 rootBundleId = uint32(rootBundles.length);
         RootBundle storage rootBundle = rootBundles.push();
         rootBundle.relayerRefundRoot = relayerRefundRoot;
```

### contracts/chain-adapters/Arbitrum_Adapter.sol
```diff
@@ -33,6 +33,10 @@ interface ArbitrumL1ERC20GatewayLike {
 
 /**
  * @notice Contract containing logic to send messages from L1 to Arbitrum.
+ * @dev Public functions calling external contracts do not guard against reentrancy because they are expected to be
+ * called via delegatecall, which will execute this contract's logic within the context of the originating contract.
+ * For example, the HubPool will delegatecall these functions, therefore its only neccessary that the HubPool's methods
+ * that call this contract's logic guard against reentrancy.
  */
 contract Arbitrum_Adapter is AdapterInterface {
     // Gas limit for immediate L2 execution attempt (can be estimated via NodeInterface.estimateRetryableTicket).
```

### contracts/chain-adapters/CrossDomainEnabled.sol
```diff
@@ -7,6 +7,8 @@ import { ICrossDomainMessenger } from "@eth-optimism/contracts/libraries/bridge/
 /**
  * @title CrossDomainEnabled
  * @dev Helper contract for contracts performing cross-domain communications between L1 and Optimism.
+ * @dev This modifies the eth-optimism/CrossDomainEnabled contract only by changing state variables to be
+ * immutable for use in contracts like the Optimism_Adapter which use delegateCall().
  */
 contract CrossDomainEnabled {
     // Messenger contract used to send and recieve messages from the other domain.
```

### contracts/chain-adapters/Ethereum_Adapter.sol
```diff
@@ -4,8 +4,6 @@ pragma solidity ^0.8.0;
 import "../interfaces/AdapterInterface.sol";
 import "../interfaces/WETH9.sol";
 
-import "@uma/core/contracts/common/implementation/Lockable.sol";
-
 import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
 import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
 
@@ -15,6 +13,10 @@ import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
  * contract between HubPool and SpokePool on the same chain. Its named "Ethereum_Adapter" because a core assumption
  * is that the HubPool will be deployed on Ethereum, so this adapter will be used to communicate between HubPool
  * and the Ethereum_SpokePool.
+ * @dev Public functions calling external contracts do not guard against reentrancy because they are expected to be
+ * called via delegatecall, which will execute this contract's logic within the context of the originating contract.
+ * For example, the HubPool will delegatecall these functions, therefore its only neccessary that the HubPool's methods
+ * that call this contract's logic guard against reentrancy.
  */
 contract Ethereum_Adapter is AdapterInterface {
     using SafeERC20 for IERC20;
```

### contracts/chain-adapters/Optimism_Adapter.sol
```diff
@@ -4,16 +4,20 @@ pragma solidity ^0.8.0;
 import "../interfaces/AdapterInterface.sol";
 import "../interfaces/WETH9.sol";
 
+// @dev Use local modified CrossDomainEnabled contract instead of one exported by eth-optimism because we need
+// this contract's state variables to be `immutable` because of the delegateCall call.
 import "./CrossDomainEnabled.sol";
 import "@eth-optimism/contracts/L1/messaging/IL1StandardBridge.sol";
 
-import "@uma/core/contracts/common/implementation/Lockable.sol";
-
 import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
 import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
 
 /**
  * @notice Contract containing logic to send messages from L1 to Optimism.
+ * @dev Public functions calling external contracts do not guard against reentrancy because they are expected to be
+ * called via delegatecall, which will execute this contract's logic within the context of the originating contract.
+ * For example, the HubPool will delegatecall these functions, therefore its only neccessary that the HubPool's methods
+ * that call this contract's logic guard against reentrancy.
  */
 contract Optimism_Adapter is CrossDomainEnabled, AdapterInterface {
     using SafeERC20 for IERC20;
```

### contracts/chain-adapters/Polygon_Adapter.sol
```diff
@@ -3,10 +3,10 @@ pragma solidity ^0.8.0;
 
 import "../interfaces/AdapterInterface.sol";
 import "../interfaces/WETH9.sol";
+import "../Lockable.sol";
 
 import "@eth-optimism/contracts/libraries/bridge/CrossDomainEnabled.sol";
 import "@eth-optimism/contracts/L1/messaging/IL1StandardBridge.sol";
-import "../Lockable.sol";
 import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
 import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
 
@@ -26,6 +26,10 @@ interface IFxStateSender {
 
 /**
  * @notice Sends cross chain messages Polygon L2 network.
+ * @dev Public functions calling external contracts do not guard against reentrancy because they are expected to be
+ * called via delegatecall, which will execute this contract's logic within the context of the originating contract.
+ * For example, the HubPool will delegatecall these functions, therefore its only neccessary that the HubPool's methods
+ * that call this contract's logic guard against reentrancy.
  */
 contract Polygon_Adapter is AdapterInterface {
     using SafeERC20 for IERC20;
```
