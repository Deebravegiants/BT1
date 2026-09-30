# [?] Add Reentrancy-Guard modifier to external MP methods (#1334)

## Summary
Severity: Unknown
Chain: UMA
Component: UMAprotocol/protocol
Published: 2020-05-05
Source: https://github.com/UMAprotocol/protocol/commit/f561463cfe056db94c9d8be6ec5a67b768ff6839
Type: security-commit

## Details
Add Reentrancy-Guard modifier to external MP methods (#1334)

Signed-off-by: Nick Pai <npai.nyc@gmail.com>

## Patch
### ci/run_slither.sh
```diff
@@ -14,7 +14,7 @@ run_slither() {
 
     # print out slither version for debugging
     slither --version
-    slither --exclude=divide-before-multiply,locked-ether,unused-return,timestamp,naming-convention,pragma,solc-version,external-function,reentrancy-benign,reentrancy-no-eth,arbitrary-send,incorrect-equality,reentrancy-events,assembly --filter-paths="@openzeppelin|WETH9.sol" $1
+    slither --exclude=divide-before-multiply,locked-ether,unused-return,timestamp,naming-convention,pragma,solc-version,external-function,reentrancy-benign,reentrancy-no-eth,arbitrary-send,incorrect-equality,reentrancy-events,assembly --filter-paths="@openzeppelin|WETH9.sol|ReentrancyAttack.sol|ReentrancyMock.sol" $1
 }
 
 run_slither $PROTOCOL_DIR/core
```

### core/contracts/common/implementation/AddressWhitelist.sol
```diff
@@ -1,12 +1,13 @@
 pragma solidity ^0.6.0;
 
 import "@openzeppelin/contracts/access/Ownable.sol";
+import "./Lockable.sol";
 
 
 /**
  * @title A contract to track a whitelist of addresses.
  */
-contract AddressWhitelist is Ownable {
+contract AddressWhitelist is Ownable, Lockable {
     enum Status { None, In, Out }
     mapping(address => Status) public whitelist;
 
@@ -19,7 +20,7 @@ contract AddressWhitelist is Ownable {
      * @notice Adds an address to the whitelist.
      * @param newElement the new address to add.
      */
-    function addToWhitelist(address newElement) external onlyOwner {
+    function addToWhitelist(address newElement) external nonReentrant() onlyOwner {
         // Ignore if address is already included
         if (whitelist[newElement] == Status.In) {
             return;
@@ -39,7 +40,7 @@ contract AddressWhitelist is Ownable {
      * @notice Removes an address from the whitelist.
      * @param elementToRemove the existing address to remove.
      */
-    function removeFromWhitelist(address elementToRemove) external onlyOwner {
+    function removeFromWhitelist(address elementToRemove) external nonReentrant() onlyOwner {
         if (whitelist[elementToRemove] != Status.Out) {
             whitelist[elementToRemove] = Status.Out;
             emit RemovedFromWhitelist(elementToRemove);
@@ -51,7 +52,7 @@ contract AddressWhitelist is Ownable {
      * @param elementToCheck the address to check.
      * @return True if `elementToCheck` is on the whitelist, or False.
      */
-    function isOnWhitelist(address elementToCheck) external view returns (bool) {
+    function isOnWhitelist(address elementToCheck) external view nonReentrantView() returns (bool) {
         return whitelist[elementToCheck] == Status.In;
     }
 
@@ -63,7 +64,7 @@ contract AddressWhitelist is Ownable {
      * the empty index.
      * @return activeWhitelist the list of addresses on the whitelist.
      */
-    function getWhitelist() external view returns (address[] memory activeWhitelist) {
+    function getWhitelist() external view nonReentrantView() returns (address[] memory activeWhitelist) {
         // Determine size of whitelist first
         uint256 activeCount = 0;
         for (uint256 i = 0; i < whitelistIndices.length; i++) {
```

### core/contracts/common/implementation/Lockable.sol
```diff
@@ -0,0 +1,63 @@
+pragma solidity ^0.6.0;
+
+
+/**
+ * @title A contract that provides modifiers to prevent reentrancy to state-changing and view-only methods. This contract
+ * is inspired by https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/ReentrancyGuard.sol
+ * and https://github.com/balancer-labs/balancer-core/blob/master/contracts/BPool.sol.
+ */
+contract Lockable {
+    bool private _notEntered;
+
+    constructor() internal {
+        // Storing an initial non-zero value makes deployment a bit more
+        // expensive, but in exchange the refund on every call to nonReentrant
+        // will be lower in amount. Since refunds are capped to a percetange of
+        // the total transaction's gas, it is best to keep them low in cases
+        // like this one, to increase the likelihood of the full refund coming
+        // into effect.
+        _notEntered = true;
+    }
+
+    /**
+     * @dev Prevents a contract from calling itself, directly or indirectly.
+     * Calling a `nonReentrant` function from another `nonReentrant`
+     * function is not supported. It is possible to prevent this from happening
+     * by making the `nonReentrant` function external, and make it call a
+     * `private` function that does the actual work.
+     */
+    modifier nonReentrant() {
+        _preEntranceCheck();
+        _preEntranceSet();
+        _;
+        _postEntranceReset();
+    }
+
+    /**
+     * @dev Designed to prevent a view-only method from being re-entered during a call to a `nonReentrant()` state-changing method.
+     */
+    modifier nonReentrantView() {
+        _preEntranceCheck();
+        _;
+    }
+
+    // Internal methods are used to avoid copying the require statement's bytecode to every `nonReentrant()` method.
+    // On entry into a function, `_preEntranceCheck()` should always be called to check if the function is being re-entered.
+    // Then, if the function modifies state, it should call `_postEntranceSet()`, perform its logic, and then call `_postEntranceReset()`.
+    // View-only methods can simply call `_preEntranceCheck()` to make sure that it is not being re-entered.
+    function _preEntranceCheck() internal view {
+        // On the first call to nonReentrant, _notEntered will be true
+        require(_notEntered, "ReentrancyGuard: reentrant call");
+    }
+
+    function _preEntranceSet() internal {
+        // Any calls to nonReentrant after this point will fail
+        _notEntered = false;
+    }
+
+    function _postEntranceReset() internal {
+        // By storing the original value once again, a refund is triggered (see
+        // https://eips.ethereum.org/EIPS/eip-2200)
+        _notEntered = true;
+    }
+}
```

### core/contracts/common/test/ReentrancyAttack.sol
```diff
@@ -0,0 +1,12 @@
+pragma solidity ^0.6.0;
+
+
+// Tests reentrancy guards defined in Lockable.sol.
+// Copied from https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v3.0.1/contracts/mocks/ReentrancyAttack.sol.
+contract ReentrancyAttack {
+    function callSender(bytes4 data) public {
+        // solhint-disable-next-line avoid-low-level-calls
+        (bool success, ) = msg.sender.call(abi.encodeWithSelector(data));
+        require(success, "ReentrancyAttack: failed call");
+    }
+}
```

### core/contracts/common/test/ReentrancyMock.sol
```diff
@@ -0,0 +1,65 @@
+pragma solidity ^0.6.0;
+
+import "../implementation/Lockable.sol";
+import "./ReentrancyAttack.sol";
+
+
+// Tests reentrancy guards defined in Lockable.sol.
+// Extends https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v3.0.1/contracts/mocks/ReentrancyMock.sol.
+contract ReentrancyMock is Lockable {
+    uint256 public counter;
+
+    constructor() public {
+        counter = 0;
+    }
+
+    function callback() external nonReentrant {
+        _count();
+    }
+
+    function countAndSend(ReentrancyAttack attacker) external nonReentrant {
+        _count();
+        bytes4 func = bytes4(keccak256("callback()"));
+        attacker.callSender(func);
+    }
+
+    function countAndCall(ReentrancyAttack attacker) external nonReentrant {
+        _count();
+        bytes4 func = bytes4(keccak256("getCount()"));
+        attacker.callSender(func);
+    }
+
+    function countLocalRecursive(uint256 n) public nonReentrant {
+        if (n > 0) {
+            _count();
+            countLocalRecursive(n - 1);
+        }
+    }
+
+    function countThisRecursive(uint256 n) public nonReentrant {
+        if (n > 0) {
+            _count();
+            // solhint-disable-next-line avoid-low-level-calls
+            (bool success, ) = address(this).call(abi.encodeWithSignature("countThisRecursive(uint256)", n - 1));
+            require(success, "ReentrancyMock: failed call");
+        }
+    }
+
+    function countLocalCall() public nonReentrant {
+        getCount();
+    }
+
+    function countThisCall() public nonReentrant {
+        // solhint-disable-next-line avoid-low-level-calls
+        (bool success, ) = address(this).call(abi.encodeWithSignature("getCount()"));
+        require(success, "ReentrancyMock: failed call");
+    }
+
+    function getCount() public view nonReentrantView returns (uint256) {
+        return counter;
+    }
+
+    function _count() private {
+        counter += 1;
+    }
+}
```

### core/contracts/financial-templates/implementation/ExpiringMultiParty.sol
```diff
@@ -5,5 +5,5 @@ import "./Liquidatable.sol";
 
 
 contract ExpiringMultiParty is Liquidatable {
-    constructor(ConstructorParams memory params) public Liquidatable(params) {}
+    constructor(ConstructorParams memory params) public Liquidatable(params) nonReentrant() {}
 }
```

### core/contracts/financial-templates/implementation/ExpiringMultiPartyCreator.sol
```diff
@@ -4,6 +4,7 @@ pragma experimental ABIEncoderV2;
 import "../../oracle/implementation/ContractCreator.sol";
 import "../../common/implementation/Testable.sol";
 import "../../common/implementation/AddressWhitelist.sol";
+import "../../common/implementation/Lockable.sol";
 import "./ExpiringMultiPartyLib.sol";
 
 
@@ -12,7 +13,7 @@ import "./ExpiringMultiPartyLib.sol";
  * @notice Factory contract to create and register new instances of expiring multiparty contracts.
  * Responsible for constraining the parameters used to construct a new EMP.
  */
-contract ExpiringMultiPartyCreator is ContractCreator, Testable {
+contract ExpiringMultiPartyCreator is ContractCreator, Testable, Lockable {
     using FixedPoint for FixedPoint.Unsigned;
 
     /****************************************
@@ -82,7 +83,7 @@ contract ExpiringMultiPartyCreator is ContractCreator, Testable {
         address _collateralTokenWhitelist,
         address _tokenFactoryAddress,
         address _timerAddress
-    ) public ContractCreator(_finderAddress) Testable(_timerAddress) {
+    ) public ContractCreator(_finderAddress) Testable(_timerAddress) nonReentrant() {
         collateralTokenWhitelist = AddressWhitelist(_collateralTokenWhitelist);
         tokenFactoryAddress = _tokenFactoryAddress;
         uint32[16] memory timestamps = [
@@ -113,7 +114,7 @@ contract ExpiringMultiPartyCreator is ContractCreator, Testable {
      * @param params is a `ConstructorParams` object from ExpiringMultiParty.
      * @return address of the deployed ExpiringMultiParty contract
      */
-    function createExpiringMultiParty(Params memory params) public returns (address) {
+    function createExpiringMultiParty(Params memory params) public nonReentrant() returns (address) {
         address derivative = ExpiringMultiPartyLib.deploy(_convertParams(params));
 
         _registerContract(new address[](0), address(derivative));
```

### core/contracts/financial-templates/implementation/FeePayer.sol
```diff
@@ -3,6 +3,7 @@ pragma experimental ABIEncoderV2;
 
 import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
 import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
+import "../../common/implementation/Lockable.sol";
 import "../../common/implementation/FixedPoint.sol";
 import "../../common/implementation/Testable.sol";
 import "../../oracle/interfaces/StoreInterface.sol";
@@ -16,7 +17,7 @@ import "../../oracle/implementation/Constants.sol";
  * contract is abstract as each derived contract that inherits `FeePayer` must implement `pfc()`.
  */
 
-abstract contract FeePayer is Testable {
+abstract contract FeePayer is Testable, Lockable {
     using SafeMath for uint256;
     using FixedPoint for FixedPoint.Unsigned;
     using SafeERC20 for IERC20;
@@ -71,7 +72,7 @@ abstract contract FeePayer is Testable {
         address _collateralAddress,
         address _finderAddress,
         address _timerAddress
-    ) public Testable(_timerAddress) {
+    ) public Testable(_timerAddress) nonReentrant() {
         collateralCurrency = IERC20(_collateralAddress);
         finder = FinderInterface(_finderAddress);
         lastPaymentTime = getCurrentTime();
@@ -83,20 +84,20 @@ abstract contract FeePayer is Testable {
      ****************************************/
 
     /**
-     * @notice Pays UMA DVM regular fees to the Store contract.
+     * @notice Pays UMA DVM regular fees (as a % of the collateral pool) to the Store contract.
      * @dev These must be paid periodically for the life of the contract. If the contract has not paid its
      * regular fee in a week or more then a late penalty is applied which is sent to the caller.
      * This will revert if the amount of fees owed are greater than the pfc. An event is only fired if the fees charged are greater than 0.
      * @return totalPaid Amount of collateral that the contract paid (sum of the amount paid to the Store and caller).
      * This will return 0 and exit early if there is no pfc, fees were already paid during the current block, or the fee rate is 0.
      */
-    function payRegularFees() public returns (FixedPoint.Unsigned memory totalPaid) {
+    function payRegularFees() public nonReentrant() returns (FixedPoint.Unsigned memory totalPaid) {
         StoreInterface store = _getStore();
         uint256 time = getCurrentTime();
-        FixedPoint.Unsigned memory _pfc = pfc();
+        FixedPoint.Unsigned memory collateralPool = _pfc();
 
-        // Exit early if there is no pfc (thus, no fees to be paid).
-        if (_pfc.isEqual(0)) {
+        // Exit early if there is no collateral from which to pay fees.
+        if (collateralPool.isEqual(0)) {
             return totalPaid;
         }
 
@@ -108,7 +109,7 @@ abstract contract FeePayer is Testable {
         (FixedPoint.Unsigned memory regularFee, FixedPoint.Unsigned memory latePenalty) = store.computeRegularFee(
             lastPaymentTime,
             time,
-            _pfc
+            collateralPool
         );
         lastPaymentTime = time;
 
@@ -130,8 +131,7 @@ abstract contract FeePayer is Testable {
 
         emit RegularFeesPaid(regularFee.rawValue, latePenalty.rawValue);
 
-        // Adjust the cumulative fee multiplier by the fee paid and the current PFC.
-        _adjustCumulativeFeeMultiplier(totalPaid, _pfc);
+        _adjustCumulativeFeeMultiplier(totalPaid, collateralPool);
 
         if (regularFee.isGreaterThan(0)) {
             collateralCurrency.safeIncreaseAllowance(address(store), regularFee.rawValue);
@@ -156,13 +156,12 @@ abstract contract FeePayer is Testable {
             collateralCurrency.safeTransferFrom(payer, address(this), amount.rawValue);
         } else {
             // If the payer is the contract, adjust the cumulativeFeeMultiplier to compensate.
-            FixedPoint.Unsigned memory _pfc = pfc();
+            FixedPoint.Unsigned memory collateralPool = _pfc();
 
-            // The final fee must be < pfc or the fee will be larger than 100%.
-            require(_pfc.isGreaterThan(amount), "Final fee is more than PfC");
+            // The final fee must be < available collateral or the fee will be larger than 100%.
+            require(collateralPool.isGreaterThan(amount), "Final fee is more than PfC");
 
-            // Adjust the cumulative fee multiplier by the fee paid and the current PFC.
-            _adjustCumulativeFeeMultiplier(amount, _pfc);
+            _adjustCumulativeFeeMultiplier(amount, collateralPool);
         }
 
         emit FinalFeesPaid(amount.rawValue);
@@ -174,15 +173,20 @@ abstract contract FeePayer is Testable {
 
     /**
      * @notice Gets the current profit from corruption for this contract in terms of the collateral currency.
-     * @dev Derived contracts are expected to implement this function so the payRegularFees()
-     * method can correctly compute the owed regular fees.
+     * @dev This will be equivalent to the collateral pool available from which to pay fees.
+     * Therefore, derived contracts are expected to implement this so that pay-fee methods
+     * can correctly compute the owed fees as a % of PfC.
      */
-    function pfc() public virtual view returns (FixedPoint.Unsigned memory);
+    function pfc() public view nonReentrantView() returns (FixedPoint.Unsigned memory) {
+        return _pfc();
+    }
 
     /****************************************
      *         INTERNAL FUNCTIONS           *
      ****************************************/
 
+    function _pfc() internal virtual view returns (FixedPoint.Unsigned memory);
+
     function _getStore() internal view returns (StoreInterface) {
         return StoreInterface(finder.getImplementationAddress(OracleInterfaces.Store));
     }
@@ -246,7 +250,7 @@ abstract contract FeePayer is Testable {
         addedCollateral = _getFeeAdjustedCollateral(rawCollateral).sub(initialBalance);
     }
 
-    // Scale the cumulativeFeeMultiplier by the ratio of fees paid to the current profit from corruption.
+    // Scale the cumulativeFeeMultiplier by the ratio of fees paid to the current available collateral.
     function _adjustCumulativeFeeMultiplier(FixedPoint.Unsigned memory amount, FixedPoint.Unsigned memory currentPfc)
         internal
     {
```

### core/contracts/financial-templates/implementation/Liquidatable.sol
```diff
@@ -156,6 +156,7 @@ contract Liquidatable is PricelessPositionManager {
             params.minSponsorTokens,
             params.timerAddress
         )
+        nonReentrant()
     {
         require(params.collateralRequirement.isGreaterThan(1), "CR is more than 100%");
         require(
@@ -195,6 +196,7 @@ contract Liquidatable is PricelessPositionManager {
         external
         fees()
         onlyPreExpiration()
+        nonReentrant()
         returns (
             uint256 liquidationId,
             FixedPoint.Unsigned memory tokensLiquidated,
@@ -306,6 +308,7 @@ contract Liquidatable is PricelessPositionManager {
         external
         disputable(liquidationId, sponsor)
         fees()
+        nonReentrant()
         returns (FixedPoint.Unsigned memory totalPaid)
     {
         LiquidationData storage disputedLiquidation = _getLiquidationData(sponsor, liquidationId);
@@ -354,6 +357,7 @@ contract Liquidatable is PricelessPositionManager {
         public
         withdrawable(liquidationId, sponsor)
         fees()
+        nonReentrant()
         returns (FixedPoint.Unsigned memory amountWithdrawn)
     {
         LiquidationData storage liquidation = _getLiquidationData(sponsor, liquidationId);
@@ -444,14 +448,7 @@ contract Liquidatable is PricelessPositionManager {
         collateralCurrency.safeTransfer(msg.sender, amountWithdrawn.rawValue);
     }
 
-    /**
-     * @dev This overrides pfc() so the Liquidatable contract can report its profit from corruption.
-     */
-    function pfc() public override view returns (FixedPoint.Unsigned memory) {
-        return super.pfc().add(_getFeeAdjustedCollateral(rawLiquidationCollateral));
-    }
-
-    function getLiquidations(address sponsor) external view returns (LiquidationData[] memory) {
+    function getLiquidations(address sponsor) external view nonReentrantView() returns (LiquidationData[] memory) {
         return liquidations[sponsor];
     }
 
@@ -496,6 +493,10 @@ contract Liquidatable is PricelessPositionManager {
         );
     }
 
+    function _pfc() internal override view returns (FixedPoint.Unsigned memory) {
+        return super._pfc().add(_getFeeAdjustedCollateral(rawLiquidationCollateral));
+    }
+
     function _getLiquidationData(address sponsor, uint256 liquidationId)
         internal
         view
```

### core/contracts/financial-templates/implementation/PricelessPositionManager.sol
```diff
@@ -158,7 +158,7 @@ contract PricelessPositionManager is FeePayer, AdministrateeInterface {
         address _tokenFactoryAddress,
         FixedPoint.Unsigned memory _minSponsorTokens,
         address _timerAddress
-    ) public FeePayer(_collateralAddress, _finderAddress, _timerAddress) {
+    ) public FeePayer(_collateralAddress, _finderAddress, _timerAddress) nonReentrant() {
         require(_expirationTimestamp > getCurrentTime(), "Invalid expiration in future");
         require(_getIdentifierWhitelist().isIdentifierSupported(_priceIdentifier), "Unsupported price identifier");
 
@@ -179,7 +179,7 @@ contract PricelessPositionManager is FeePayer, AdministrateeInterface {
      * Once the request liveness is passed, the sponsor can execute the transfer.
      * @dev The liveness length is the same as the withdrawal liveness.
      */
-    function requestTransferPosition() public onlyPreExpiration() {
+    function requestTransferPosition() public onlyPreExpiration() nonReentrant() {
         PositionData storage positionData = _getPositionData(msg.sender);
         require(positionData.transferPositionRequestPassTimestamp == 0, "Pending transfer");
 
@@ -203,6 +203,7 @@ contract PricelessPositionManager is FeePayer, AdministrateeInterface {
         public
         onlyPreExpiration()
         noPendingWithdrawal(msg.sender)
+        nonReentrant()
     {
         require(
             _getFeeAdjustedCollateral(positions[newSponsorAddress].rawCollateral).isEqual(
@@ -231,7 +232,7 @@ contract PricelessPositionManager is FeePayer, AdministrateeInterface {
     /**
      * @notice Cancels a pending transfer position request.
      */
-    function cancelTransferPosition() external onlyPreExpiration() {
+    function cancelTransferPosition() external onlyPreExpiration() nonReentrant() {
         PositionData storage positionData = _getPositionData(msg.sender);
         require(positionData.transferPositionRequestPassTimestamp != 0, "No pending transfer");
 
@@ -252,6 +253,7 @@ contract PricelessPositionManager is FeePayer, AdministrateeInterface {
         onlyPreExpiration()
         noPendingWithdrawal(msg.sender)
         fees()
+        nonReentrant()
     {
         require(collateralAmount.isGreaterThan(0), "Invalid collateral amount");
         PositionData storage positionData = _getPositionData(msg.sender);
@@ -278,6 +280,7 @@ contract PricelessPositionManager is FeePayer, AdministrateeInterface {
         onlyPreExpiration()
         noPendingWithdrawal(msg.sender)
         fees()
+        nonReentrant()
         returns (FixedPoint.Unsigned memory amountWithdrawn)
     {
         PositionData storage positionData = _getPositionData(msg.sender);
@@ -306,6 +309,7 @@ contract PricelessPositionManager is FeePayer, AdministrateeInterface {
         public
         onlyPreExpiration()
         noPendingWithdrawal(msg.sender)
+        nonReentrant()
     {
         PositionData storage positionData = _getPositionData(msg.sender);
         require(
@@ -336,6 +340,7 @@ contract PricelessPositionManager is FeePayer, AdministrateeInterface {
         external
         onlyPreExpiration()
         fees()
+        nonReentrant()
         returns (FixedPoint.Unsigned memory amountWithdrawn)
     {
         PositionData storage positionData = _getPositionData(msg.sender);
@@ -366,7 +371,7 @@ contract PricelessPositionManager is FeePayer, AdministrateeInterface {
     /**
      * @notice Cancels a pending withdrawal request.
      */
-    function cancelWithdrawal() external onlyPreExpiration() {
+    function cancelWithdrawal() external onlyPreExpiration() nonReentrant() {
         PositionData storage positionData = _getPositionData(msg.sender);
         require(positionData.requestPassTimestamp != 0, "No pending withdrawal");
 
@@ -388,6 +393,7 @@ contract PricelessPositionManager is FeePayer, AdministrateeInterface {
         public
         onlyPreExpiration()
         fees()
+        nonReentrant()
     {
         require(_checkCollateralization(collateralAmount, numTokens), "CR below GCR");
 
@@ -426,6 +432,7 @@ contract PricelessPositionManager is FeePayer, AdministrateeInterface {
         onlyPreExpiration()
         noPendingWithdrawal(msg.sender)
         fees()
+        nonReentrant()
         returns (FixedPoint.Unsigned memory amountWithdrawn)
     {
         PositionData storage positionData = _getPositionData(msg.sender);
@@ -469,7 +476,13 @@ contract PricelessPositionManager is FeePayer, AdministrateeInterface {
      * caller's full balance.
      * @return amountWithdrawn The actual amount of collateral withdrawn.
      */
-    function settleExpired() external onlyPostExpiration() fees() returns (FixedPoint.Unsigned memory amountWithdrawn) {
+    function settleExpired()
+        external
+        onlyPostExpiration()
+        fees()
+        nonReentrant()
+        returns (FixedPoint.Unsigned memory amountWithdrawn)
+    {
         // If the contract state is open and onlyPostExpiration passed then `expire()` has not yet been called.
         require(contractState != ContractState.Open, "Unexpired position");
 
@@ -533,7 +546,7 @@ contract PricelessPositionManager is FeePayer, AdministrateeInterface {
      * @dev this function can only be called once the contract is expired and cant be re-called
      * due to the state modifiers applied on it.
      */
-    function expire() external onlyPostExpiration() onlyOpenState() fees() {
+    function expire() external onlyPostExpiration() onlyOpenState() fees() nonReentrant() {
         contractState = ContractState.ExpiredPriceRequested;
 
         // The final fee for this request is paid out of the contract rather than by the caller.
@@ -551,7 +564,7 @@ contract PricelessPositionManager is FeePayer, AdministrateeInterface {
      * which prevents re-entry into this function or the `expire` function. No fees are paid when calling
      * `emergencyShutdown` as the governor who would call the function would also receive the fees.
      */
-    function emergencyShutdown() external override onlyPreExpiration() onlyOpenState() {
+    function emergencyShutdown() external override onlyPreExpiration() onlyOpenState() nonReentrant() {
         require(msg.sender == _getFinancialContractsAdminAddress(), "Caller not Governor");
 
         contractState = ContractState.ExpiredPriceRequested;
@@ -564,7 +577,7 @@ contract PricelessPositionManager is FeePayer, AdministrateeInterface {
         emit EmergencyShutdown(msg.sender, oldExpirationTimestamp, expirationTimestamp);
     }
 
-    function remargin() external override onlyPreExpiration() {
+    function remargin() external override onlyPreExpiration() nonReentrant() {
         return;
     }
 
@@ -574,22 +587,15 @@ contract PricelessPositionManager is FeePayer, AdministrateeInterface {
      * rawCollateral, which isn't a user-readable value.
      * @param sponsor address whose collateral amount is retrieved.
      */
-    function getCollateral(address sponsor) external view returns (FixedPoint.Unsigned memory) {
+    function getCollateral(address sponsor) external view nonReentrantView() returns (FixedPoint.Unsigned memory) {
         // Note: do a direct access to avoid the validity check.
         return _getFeeAdjustedCollateral(positions[sponsor].rawCollateral);
     }
 
     /**
      * @notice Accessor method for the total collateral stored within the PricelessPositionManager.
      */
-    function totalPositionCollateral() external view returns (FixedPoint.Unsigned memory) {
-        return _getFeeAdjustedCollateral(rawTotalPositionCollateral);
-    }
-
-    /**
-     * @dev This overrides pfc() so the PricelessPositionManager can report its profit from corruption.
-     */
-    function pfc() public virtual override view returns (FixedPoint.Unsigned memory) {
+    function totalPositionCollateral() external view nonReentrantView() returns (FixedPoint.Unsigned memory) {
         return _getFeeAdjustedCollateral(rawTotalPositionCollateral);
     }
 
@@ -651,6 +657,10 @@ contract PricelessPositionManager is FeePayer, AdministrateeInterface {
         return startingGlobalCollateral.sub(_getFeeAdjustedCollateral(rawTotalPositionCollateral));
     }
 
+    function _pfc() internal virtual override view returns (FixedPoint.Unsigned memory) {
+        return _getFeeAdjustedCollateral(rawTotalPositionCollateral);
+    }
+
     function _getPositionData(address sponsor)
         internal
         view
```

### core/contracts/financial-templates/implementation/SyntheticToken.sol
```diff
@@ -1,5 +1,6 @@
 pragma solidity ^0.6.0;
 import "../../common/implementation/ExpandedERC20.sol";
+import "../../common/implementation/Lockable.sol";
 
 
 /**
@@ -8,7 +9,7 @@ import "../../common/implementation/ExpandedERC20.sol";
  * well as the owner who is capable of adding new roles.
  */
 
-contract SyntheticToken is ExpandedERC20 {
+contract SyntheticToken is ExpandedERC20, Lockable {
     /**
      * @notice Constructs the SyntheticToken.
      * @param tokenName The name which describes the new token.
@@ -19,14 +20,14 @@ contract SyntheticToken is ExpandedERC20 {
         string memory tokenName,
         string memory tokenSymbol,
         uint8 tokenDecimals
-    ) public ExpandedERC20(tokenName, tokenSymbol, tokenDecimals) {}
+    ) public ExpandedERC20(tokenName, tokenSymbol, tokenDecimals) nonReentrant() {}
 
     /**
      * @notice Add Minter role to account.
      * @dev The caller must have the Owner role.
      * @param account The address to which the Minter role is added.
      */
-    function addMinter(address account) external {
+    function addMinter(address account) external nonReentrant() {
         addMember(uint256(Roles.Minter), account);
     }
 
@@ -35,7 +36,7 @@ contract SyntheticToken is ExpandedERC20 {
      * @dev The caller must have the Owner role.
      * @param account The address from which the Minter role is removed.
      */
-    function removeMinter(address account) external {
+    function removeMinter(address account) external nonReentrant() {
         removeMember(uint256(Roles.Minter), account);
     }
 
@@ -44,7 +45,7 @@ contract SyntheticToken is ExpandedERC20 {
      * @dev The caller must have the Owner role.
      * @param account The address to which the Burner role is added.
      */
-    function addBurner(address account) external {
+    function addBurner(address account) external nonReentrant() {
         addMember(uint256(Roles.Burner), account);
     }
 
@@ -53,7 +54,7 @@ contract SyntheticToken is ExpandedERC20 {
      * @dev The caller must have the Owner role.
      * @param account The address from which the Burner role is removed.
      */
-    function removeBurner(address account) external {
+    function removeBurner(address account) external nonReentrant() {
         removeMember(uint256(Roles.Burner), account);
     }
 
@@ -62,7 +63,7 @@ contract SyntheticToken is ExpandedERC20 {
      * @dev The caller must have the Owner role.
      * @param account The new holder of the Owner role.
      */
-    function resetOwner(address account) external {
+    function resetOwner(address account) external nonReentrant() {
         resetMember(uint256(Roles.Owner), account);
     }
 
@@ -71,7 +72,7 @@ contract SyntheticToken is ExpandedERC20 {
      * @param account The address which is checked for the Minter role.
      * @return bool True if the provided account is a Minter.
      */
-    function isMinter(address account) public view returns (bool) {
+    function isMinter(address account) public view nonReentrantView() returns (bool) {
         return holdsRole(uint256(Roles.Minter), account);
     }
 
@@ -80,7 +81,7 @@ contract SyntheticToken is ExpandedERC20 {
      * @param account The address which is checked for the Burner role.
      * @return bool True if the provided account is a Burner.
      */
-    function isBurner(address account) public view returns (bool) {
+    function isBurner(address account) public view nonReentrantView() returns (bool) {
         return holdsRole(uint256(Roles.Burner), account);
     }
 }
```

### core/contracts/financial-templates/implementation/TokenFactory.sol
```diff
@@ -1,13 +1,15 @@
 pragma solidity ^0.6.0;
+
 import "./SyntheticToken.sol";
 import "../../common/interfaces/ExpandedIERC20.sol";
+import "../../common/implementation/Lockable.sol";
 
 
 /**
  * @title Factory for creating new mintable and burnable tokens.
  */
 
-contract TokenFactory {
+contract TokenFactory is Lockable {
     /**
      * @notice Create a new token and return it to the caller.
      * @dev The caller will become the only minter and burner and the new owner capable of assigning the roles.
@@ -20,7 +22,7 @@ contract TokenFactory {
         string calldata tokenName,
         string calldata tokenSymbol,
         uint8 tokenDecimals
-    ) external returns (ExpandedIERC20 newToken) {
+    ) external nonReentrant() returns (ExpandedIERC20 newToken) {
         SyntheticToken mintableToken = new SyntheticToken(tokenName, tokenSymbol, tokenDecimals);
         mintableToken.addMinter(msg.sender);
         mintableToken.addBurner(msg.sender);
```
