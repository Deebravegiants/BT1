# [?] Merge pull request #107 from debridge-finance/fix/add-reentrancy-init

## Summary
Severity: Unknown
Chain: Bridge
Component: debridge-finance/debridge-contracts-v1
Published: 2021-11-01
Source: https://github.com/debridge-finance/debridge-contracts-v1/commit/736159b8eb6eca3a799b0c0d6a0c82e41cc44384
Type: security-commit

## Details
Merge pull request #107 from debridge-finance/fix/add-reentrancy-init

Small fixes

## Patch
### contracts/interfaces/IDeBridgeGate.sol
```diff
@@ -25,11 +25,6 @@ interface IDeBridgeGate {
         mapping(uint256 => uint256) getChainFee; // whether the chain for the asset is supported
     }
 
-    struct AggregatorInfo {
-        address aggregator; // aggregator address
-        bool isValid; // if is still valid
-    }
-
     struct ChainSupportInfo {
         uint256 fixedNativeFee; // transfer fixed fee
         bool isSupported; // whether the chain for the asset is supported
```

### contracts/mock/MockFlashCallBack.sol
```diff
@@ -13,8 +13,8 @@ contract MockFlashCallback {
     bool public revertOrNo;
 
     /// @param fee The fee amount in token due to the pool by the end of the flash
-    /// @param data Any data passed through by the caller via the IDeBridgeGate#flash call
-    function flashCallback(uint256 fee, bytes calldata data) external {
+    // /// @param data Any data passed through by the caller via the IDeBridgeGate#flash call
+    function flashCallback(uint256 fee, bytes calldata /* data */) external {
         if (revertOrNo) {
             IERC20(lastTokenAddress).safeTransfer(lastFlashReceiver, lastAmount);
         } else {
```

### contracts/mock/MockPriceConsumer.sol
```diff
@@ -59,8 +59,8 @@ contract MockPriceConsumer is IPriceConsumer, Ownable, Initializable {
     }
 
     function getPairAddress(address _token0, address _token1) public view override returns (address) {
-        IUniswapV2Factory factory = IUniswapV2Factory(factory);
-        return factory.getPair(_token0, _token1);
+        IUniswapV2Factory _factory = IUniswapV2Factory(factory);
+        return _factory.getPair(_token0, _token1);
     }
 
     function addPriceFeed(address _token, uint256 _price) external onlyOwner {
```

### contracts/mock/MockStrategy.sol
```diff
@@ -10,19 +10,30 @@ contract MockStrategy is IStrategy {
         balance = 0;
     }
 
-    function deposit(address _token, uint256 _amount) external override {
+    // suppress "unused variable" warnings by commenting out variable names
+
+    function deposit(
+        address /* _token */,
+        uint256 _amount
+    ) external override {
         balance += _amount;
     }
 
-    function withdraw(address _token, uint256 _amount) external override {
+    function withdraw(
+        address /* _token */,
+        uint256 _amount
+    ) external override {
         balance -= _amount;
     }
 
-    function withdrawAll(address token) external override {
+    function withdrawAll(address /* token */) external override {
         balance = 0;
     }
 
-    function updateReserves(address account, address token)
+    function updateReserves(
+        address /* account */,
+        address /* token */
+    )
         external
         view
         override
@@ -31,7 +42,7 @@ contract MockStrategy is IStrategy {
         return balance;
     }
 
-    function strategyToken(address token) external view override returns(address){
+    function strategyToken(address /* token */) external pure override returns(address){
         return address(0);
     }
 }
```

### contracts/mock/MockToken.sol
```diff
@@ -18,6 +18,8 @@ contract MockToken is ERC20 {
 
     fallback() external payable { }
 
+    receive() external payable { }
+
     function mint(address _receiver, uint256 _amount) external {
         _mint(_receiver, _amount);
     }
```

### contracts/mock/aave/AaveProtocolDataProvider.sol
```diff
@@ -6,7 +6,7 @@ import {LendingPool} from "./LendingPool.sol";
 contract AaveProtocolDataProvider {
     LendingPoolAddressesProvider public immutable ADDRESSES_PROVIDER;
 
-    constructor(LendingPoolAddressesProvider addressesProvider) public {
+    constructor(LendingPoolAddressesProvider addressesProvider) {
         ADDRESSES_PROVIDER = addressesProvider;
     }
 
```

### contracts/mock/compound/MockCToken.sol
```diff
@@ -1,3 +1,4 @@
+// SPDX-License-Identifier: MIT
 pragma solidity 0.8.7;
 
 import "./Comptroller.sol";
@@ -64,7 +65,7 @@ contract MockCToken is ERC20 {
         address user,
         uint256 amount,
         uint256 index
-    ) external returns (bool) {
+    ) external {
         accountTokens[user] += amount;
         _mint(user, amount);
 
@@ -99,4 +100,4 @@ contract MockCToken is ERC20 {
     function _setComptroller(address newComptroller) public {
         comptroller = newComptroller;
     }
-}
\ No newline at end of file
+}
```

### contracts/mock/compound/MockCompoundController.sol
```diff
@@ -54,7 +54,6 @@ contract MockCompoundController is IStrategy {
 
   function withdraw(address _token, uint256 _amount) public override {
     address cToken = strategyToken(_token);
-    uint256 maxAmount = IERC20(cToken).balanceOf(msg.sender);
 
     uint256 userBalance = IERC20(cToken).balanceOf(msg.sender);
     uint256 amountToWithdraw = _amount;
```

### contracts/mock/yearn/MockYVault.sol
```diff
@@ -46,7 +46,7 @@ contract MockYearnVault is IVault {
         return ERC20(token).decimals();
     }
 
-    function pricePerShare() public view override returns (uint256) {
+    function pricePerShare() public pure override returns (uint256) {
         // TODO: increase current time like aave mocks
         return 15*1e17;
     }
```

### contracts/oracles/DelegatedStaking.sol
```diff
@@ -310,6 +310,8 @@ contract DelegatedStaking is
         swapProxy = _swapProxy;
         slashingTreasury = _slashingTreasury;
         minProfitSharingBPS = 5000;
+
+        __ReentrancyGuard_init();
     }
 
     /**
```

### contracts/periphery/FeeProxy.sol
```diff
@@ -152,7 +152,7 @@ contract FeeProxy is Initializable, AccessControlUpgradeable, PausableUpgradeabl
         uint256 chainId = getChainId();
         //DebridgeId of weth in ethereum network
         //TODO: can be set as contstant
-        (, bytes memory nativeAddress) = debridgeGate.getNativeTokenInfo(deEthToken);
+        // (, bytes memory nativeAddress) = debridgeGate.getNativeTokenInfo(deEthToken);
         if (feeProxyAddresses[chainId].length == 0) revert EmptyFeeProxyAddress(chainId);
 
         // TODO: treasuryAddresses can keep only for ETH network
```

### contracts/periphery/PriceConsumer.sol
```diff
@@ -60,7 +60,7 @@ contract PriceConsumer is IPriceConsumer, Ownable, Initializable {
     }
 
     function getPairAddress(address _token0, address _token1) public view override returns (address) {
-        IUniswapV2Factory factory = IUniswapV2Factory(factory);
-        return factory.getPair(_token0, _token1);
+        IUniswapV2Factory _factory = IUniswapV2Factory(factory);
+        return _factory.getPair(_token0, _token1);
     }
 }
```
