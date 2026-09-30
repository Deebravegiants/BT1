# [?] [IMPT][MF] Fix read-only reentrancy of Balancer

## Summary
Severity: Unknown
Chain: Pendle
Component: pendle-finance/pendle-core-v2-public
Published: 2023-04-12
Source: https://github.com/pendle-finance/pendle-core-v2-public/commit/452bb15371284992c0895ac4051e37ecd0f11261
Type: security-commit

## Details
[IMPT][MF] Fix read-only reentrancy of Balancer

## Patch
### contracts/core/StandardizedYield/implementations/BalancerStable/PendleAuraWethAnkrethSYV2.sol
```diff
@@ -1,11 +1,11 @@
 // SPDX-License-Identifier: GPL-3.0-or-later
 pragma solidity 0.8.17;
 
-import "./base/PendleAuraBalancerStableLPSY.sol";
+import "./base/PendleAuraBalancerStableLPSYV2.sol";
 import "../../../../interfaces/IWETH.sol";
 import "./base/MetaStable/MetaStablePreview.sol";
 
-contract PendleAuraWethAnkrethSY is PendleAuraBalancerStableLPSY {
+contract PendleAuraWethAnkrethSYV2 is PendleAuraBalancerStableLPSYV2 {
     address internal constant ANKRETH = 0xE95A203B1a91a908F9B9CE46459d101078c2c3cb;
     address internal constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
 
@@ -16,12 +16,14 @@ contract PendleAuraWethAnkrethSY is PendleAuraBalancerStableLPSY {
         string memory _name,
         string memory _symbol,
         MetaStablePreview _previewHelper
-    ) PendleAuraBalancerStableLPSY(_name, _symbol, LP, AURA_PID, _previewHelper) {}
+    ) PendleAuraBalancerStableLPSYV2(_name, _symbol, LP, AURA_PID, _previewHelper) {}
 
-    function _deposit(
-        address tokenIn,
-        uint256 amount
-    ) internal virtual override returns (uint256 amountSharesOut) {
+    function _deposit(address tokenIn, uint256 amount)
+        internal
+        virtual
+        override
+        returns (uint256 amountSharesOut)
+    {
         if (tokenIn == NATIVE) {
             IWETH(WETH).deposit{ value: amount }();
             amountSharesOut = super._deposit(WETH, amount);
@@ -45,21 +47,27 @@ contract PendleAuraWethAnkrethSY is PendleAuraBalancerStableLPSY {
         }
     }
 
-    function _previewDeposit(
-        address tokenIn,
-        uint256 amountTokenToDeposit
-    ) internal view virtual override returns (uint256 amountSharesOut) {
+    function _previewDeposit(address tokenIn, uint256 amountTokenToDeposit)
+        internal
+        view
+        virtual
+        override
+        returns (uint256 amountSharesOut)
+    {
         if (tokenIn == NATIVE) {
             amountSharesOut = super._previewDeposit(WETH, amountTokenToDeposit);
         } else {
             amountSharesOut = super._previewDeposit(tokenIn, amountTokenToDeposit);
         }
     }
 
-    function _previewRedeem(
-        address tokenOut,
-        uint256 amountSharesToRedeem
-    ) internal view virtual override returns (uint256 amountTokenOut) {
+    function _previewRedeem(address tokenOut, uint256 amountSharesToRedeem)
+        internal
+        view
+        virtual
+        override
+        returns (uint256 amountTokenOut)
+    {
         if (tokenOut == NATIVE) {
             amountTokenOut = super._previewRedeem(WETH, amountSharesToRedeem);
         } else {
```

### contracts/core/StandardizedYield/implementations/BalancerStable/PendleAuraWethRocketEthSYV2.sol
```diff
@@ -1,13 +1,13 @@
 // SPDX-License-Identifier: GPL-3.0-or-later
 pragma solidity 0.8.17;
 
-import "./base/PendleAuraBalancerStableLPSY.sol";
+import "./base/PendleAuraBalancerStableLPSYV2.sol";
 import "../../../../interfaces/IWETH.sol";
 import "./base/MetaStable/MetaStablePreview.sol";
 
-contract PendleAuraWethRethSY is PendleAuraBalancerStableLPSY {
-    address public constant RETH = 0xae78736Cd615f374D3085123A210448E74Fc6393;
-    address public constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
+contract PendleAuraWethRocketEthSYV2 is PendleAuraBalancerStableLPSYV2 {
+    address internal constant RETH = 0xae78736Cd615f374D3085123A210448E74Fc6393;
+    address internal constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
 
     uint256 internal constant AURA_PID = 15;
     address internal constant LP = 0x1E19CF2D73a72Ef1332C882F20534B6519Be0276;
@@ -16,12 +16,14 @@ contract PendleAuraWethRethSY is PendleAuraBalancerStableLPSY {
         string memory _name,
         string memory _symbol,
         MetaStablePreview _previewHelper
-    ) PendleAuraBalancerStableLPSY(_name, _symbol, LP, AURA_PID, _previewHelper) {}
+    ) PendleAuraBalancerStableLPSYV2(_name, _symbol, LP, AURA_PID, _previewHelper) {}
 
-    function _deposit(
-        address tokenIn,
-        uint256 amount
-    ) internal virtual override returns (uint256 amountSharesOut) {
+    function _deposit(address tokenIn, uint256 amount)
+        internal
+        virtual
+        override
+        returns (uint256 amountSharesOut)
+    {
         if (tokenIn == NATIVE) {
             IWETH(WETH).deposit{ value: amount }();
             amountSharesOut = super._deposit(WETH, amount);
@@ -34,31 +36,38 @@ contract PendleAuraWethRethSY is PendleAuraBalancerStableLPSY {
         address receiver,
         address tokenOut,
         uint256 amountSharesToRedeem
-    ) internal virtual override returns (uint256 amountTokenOut) {
+    ) internal virtual override returns (uint256) {
         if (tokenOut == NATIVE) {
-            amountTokenOut = super._redeem(address(this), WETH, amountSharesToRedeem);
+            uint256 amountTokenOut = super._redeem(address(this), WETH, amountSharesToRedeem);
             IWETH(WETH).withdraw(amountTokenOut);
             _transferOut(NATIVE, receiver, amountTokenOut);
+            return amountTokenOut;
         } else {
-            amountTokenOut = super._redeem(receiver, tokenOut, amountSharesToRedeem);
+            return super._redeem(receiver, tokenOut, amountSharesToRedeem);
         }
     }
 
-    function _previewDeposit(
-        address tokenIn,
-        uint256 amountTokenToDeposit
-    ) internal view virtual override returns (uint256 amountSharesOut) {
+    function _previewDeposit(address tokenIn, uint256 amountTokenToDeposit)
+        internal
+        view
+        virtual
+        override
+        returns (uint256 amountSharesOut)
+    {
         if (tokenIn == NATIVE) {
             amountSharesOut = super._previewDeposit(WETH, amountTokenToDeposit);
         } else {
             amountSharesOut = super._previewDeposit(tokenIn, amountTokenToDeposit);
         }
     }
 
-    function _previewRedeem(
-        address tokenOut,
-        uint256 amountSharesToRedeem
-    ) internal view virtual override returns (uint256 amountTokenOut) {
+    function _previewRedeem(address tokenOut, uint256 amountSharesToRedeem)
+        internal
+        view
+        virtual
+        override
+        returns (uint256 amountTokenOut)
+    {
         if (tokenOut == NATIVE) {
             amountTokenOut = super._previewRedeem(WETH, amountSharesToRedeem);
         } else {
```

### contracts/core/StandardizedYield/implementations/BalancerStable/PendleAuraWethWstethSYV2.sol
```diff
@@ -2,24 +2,26 @@
 pragma solidity 0.8.17;
 
 import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
-import "./base/PendleAuraBalancerStableLPSY.sol";
+import "./base/PendleAuraBalancerStableLPSYV2.sol";
 import "../../StEthHelper.sol";
 import "./base/MetaStable/MetaStablePreview.sol";
 
-contract PendleAuraWethWstethSY is PendleAuraBalancerStableLPSY, StEthHelper {
+contract PendleAuraWethWstethSYV2 is PendleAuraBalancerStableLPSYV2, StEthHelper {
     uint256 internal constant AURA_PID = 29;
     address internal constant LP = 0x32296969Ef14EB0c6d29669C550D4a0449130230;
 
     constructor(
         string memory _name,
         string memory _symbol,
         MetaStablePreview _previewHelper
-    ) PendleAuraBalancerStableLPSY(_name, _symbol, LP, AURA_PID, _previewHelper) StEthHelper() {}
+    ) PendleAuraBalancerStableLPSYV2(_name, _symbol, LP, AURA_PID, _previewHelper) StEthHelper() {}
 
-    function _deposit(
-        address tokenIn,
-        uint256 amount
-    ) internal virtual override returns (uint256 amountSharesOut) {
+    function _deposit(address tokenIn, uint256 amount)
+        internal
+        virtual
+        override
+        returns (uint256 amountSharesOut)
+    {
         if (tokenIn == NATIVE) {
             IWETH(WETH).deposit{ value: amount }();
             amountSharesOut = super._deposit(WETH, amount);
@@ -48,10 +50,13 @@ contract PendleAuraWethWstethSY is PendleAuraBalancerStableLPSY, StEthHelper {
         }
     }
 
-    function _previewDeposit(
-        address tokenIn,
-        uint256 amountTokenToDeposit
-    ) internal view virtual override returns (uint256 amountSharesOut) {
+    function _previewDeposit(address tokenIn, uint256 amountTokenToDeposit)
+        internal
+        view
+        virtual
+        override
+        returns (uint256 amountSharesOut)
+    {
         if (tokenIn == NATIVE) {
             amountSharesOut = super._previewDeposit(WETH, amountTokenToDeposit);
         } else if (tokenIn == STETH) {
@@ -62,10 +67,13 @@ contract PendleAuraWethWstethSY is PendleAuraBalancerStableLPSY, StEthHelper {
         }
     }
 
-    function _previewRedeem(
-        address tokenOut,
-        uint256 amountSharesToRedeem
-    ) internal view virtual override returns (uint256 amountTokenOut) {
+    function _previewRedeem(address tokenOut, uint256 amountSharesToRedeem)
+        internal
+        view
+        virtual
+        override
+        returns (uint256 amountTokenOut)
+    {
         if (tokenOut == NATIVE) {
             amountTokenOut = super._previewRedeem(WETH, amountSharesToRedeem);
         } else if (tokenOut == STETH) {
```

### contracts/core/StandardizedYield/implementations/BalancerStable/base/PendleAuraBalancerStableLPSYV2.sol
```diff
@@ -14,13 +14,13 @@ import "./StablePoolUserData.sol";
 import "../../../../libraries/ArrayLib.sol";
 import "../../../SYBaseWithRewards.sol";
 
-abstract contract PendleAuraBalancerStableLPSY is SYBaseWithRewards {
+abstract contract PendleAuraBalancerStableLPSYV2 is SYBaseWithRewards {
     using ArrayLib for address[];
 
-    address public constant BAL_TOKEN = 0xba100000625a3754423978a60c9317c58a424e3D;
-    address public constant AURA_TOKEN = 0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF;
-    address public constant AURA_BOOSTER = 0xA57b8d98dAE62B26Ec3bcC4a365338157060B234;
-    address public constant BALANCER_VAULT = 0xBA12222222228d8Ba445958a75a0704d566BF2C8;
+    address internal constant BAL_TOKEN = 0xba100000625a3754423978a60c9317c58a424e3D;
+    address internal constant AURA_TOKEN = 0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF;
+    address internal constant AURA_BOOSTER = 0xA57b8d98dAE62B26Ec3bcC4a365338157060B234;
+    address internal constant BALANCER_VAULT = 0xBA12222222228d8Ba445958a75a0704d566BF2C8;
 
     address public immutable balLp;
     bytes32 public immutable balPoolId;
@@ -55,9 +55,11 @@ abstract contract PendleAuraBalancerStableLPSY is SYBaseWithRewards {
         previewHelper = _previewHelper;
     }
 
-    function _getPoolInfo(
-        uint256 _auraPid
-    ) internal view returns (address _auraLp, address _auraRewardManager) {
+    function _getPoolInfo(uint256 _auraPid)
+        internal
+        view
+        returns (address _auraLp, address _auraRewardManager)
+    {
         if (_auraPid > IBooster(AURA_BOOSTER).poolLength()) revert Errors.SYBalancerInvalidPid();
         (_auraLp, , , _auraRewardManager, , ) = IBooster(AURA_BOOSTER).poolInfo(_auraPid);
     }
@@ -69,10 +71,12 @@ abstract contract PendleAuraBalancerStableLPSY is SYBaseWithRewards {
     /**
      * @notice Either wraps LP, or also joins pool using exact tokenIn
      */
-    function _deposit(
-        address tokenIn,
-        uint256 amount
-    ) internal virtual override returns (uint256 amountSharesOut) {
+    function _deposit(address tokenIn, uint256 amount)
+        internal
+        virtual
+        override
+        returns (uint256 amountSharesOut)
+    {
         if (tokenIn == balLp) {
             amountSharesOut = amount;
         } else {
@@ -100,17 +104,42 @@ abstract contract PendleAuraBalancerStableLPSY is SYBaseWithRewards {
     }
 
     function exchangeRate() external view override returns (uint256) {
+        _checkBalancerReadOnlyReentrancy();
         return IRateProvider(balLp).getRate();
     }
 
+    /// @dev The `manageUserBalance` function is a non-view function that includes a reentrancy guard.
+    /// When it is called by `staticcall`, one of two cases can occur:
+    /// 1. The function passes the reentrancy guard. In this scenario, the `status` variable is set to 2,
+    /// causing the EVM to panic (since the sub-call is a `staticcall`), resulting in a revert with
+    /// no response (i.e., `response.length == 0`).
+    /// 2. The function does not pass the reentrancy guard. In this situation, it reverts due to
+    /// error `BAL#400`, which means that `response.length = 100.`
+    /// To prevent read-only reentrancy, we simply need to verify that the revert corresponds to case 1,
+    /// rather than case 2. checking `response.length == 0` is sufficient.
+    function _checkBalancerReadOnlyReentrancy() internal view {
+        IVault.UserBalanceOp[] memory noop = new IVault.UserBalanceOp[](0);
+
+        (bool isSuccess, bytes memory response) = BALANCER_VAULT.staticcall(
+            abi.encodeWithSignature(
+                "manageUserBalance((uint8,address,uint256,address,address)[])",
+                noop
+            )
+        );
+
+        assert(!isSuccess);
+        if (response.length != 0) revert Errors.SYBalancerReentrancy();
+    }
+
     /*///////////////////////////////////////////////////////////////
                     BALANCER-RELATED FUNCTIONS
     //////////////////////////////////////////////////////////////*/
 
-    function _depositToBalancer(
-        address tokenIn,
-        uint256 amountTokenToDeposit
-    ) internal virtual returns (uint256) {
+    function _depositToBalancer(address tokenIn, uint256 amountTokenToDeposit)
+        internal
+        virtual
+        returns (uint256)
+    {
         IVault.JoinPoolRequest memory request = _assembleJoinRequest(
             tokenIn,
             amountTokenToDeposit
@@ -121,10 +150,12 @@ abstract contract PendleAuraBalancerStableLPSY is SYBaseWithRewards {
         return _selfBalance(balLp);
     }
 
-    function _assembleJoinRequest(
-        address tokenIn,
-        uint256 amountTokenToDeposit
-    ) internal view virtual returns (IVault.JoinPoolRequest memory request) {
+    function _assembleJoinRequest(address tokenIn, uint256 amountTokenToDeposit)
+        internal
+        view
+        virtual
+        returns (IVault.JoinPoolRequest memory request)
+    {
         // max amounts in
         address[] memory assets = _getPoolTokenAddresses();
 
@@ -166,10 +197,12 @@ abstract contract PendleAuraBalancerStableLPSY is SYBaseWithRewards {
         return balanceAfter - balanceBefore;
     }
 
-    function _assembleExitRequest(
-        address tokenOut,
-        uint256 amountLpToRedeem
-    ) internal view virtual returns (IVault.ExitPoolRequest memory request) {
+    function _assembleExitRequest(address tokenOut, uint256 amountLpToRedeem)
+        internal
+        view
+        virtual
+        returns (IVault.ExitPoolRequest memory request)
+    {
         address[] memory assets = _getPoolTokenAddresses();
         uint256[] memory minAmountsOut = new uint256[](assets.length);
 
@@ -201,10 +234,13 @@ abstract contract PendleAuraBalancerStableLPSY is SYBaseWithRewards {
                    PREVIEW FUNCTIONS
     //////////////////////////////////////////////////////////////*/
 
-    function _previewDeposit(
-        address tokenIn,
-        uint256 amountTokenToDeposit
-    ) internal view virtual override returns (uint256 amountSharesOut) {
+    function _previewDeposit(address tokenIn, uint256 amountTokenToDeposit)
+        internal
+        view
+        virtual
+        override
+        returns (uint256 amountSharesOut)
+    {
         if (tokenIn == balLp) {
             amountSharesOut = amountTokenToDeposit;
         } else {
@@ -222,10 +258,13 @@ abstract contract PendleAuraBalancerStableLPSY is SYBaseWithRewards {
         }
     }
 
-    function _previewRedeem(
-        address tokenOut,
-        uint256 amountSharesToRedeem
-    ) internal view virtual override returns (uint256 amountTokenOut) {
+    function _previewRedeem(address tokenOut, uint256 amountSharesToRedeem)
+        internal
+        view
+        virtual
+        override
+        returns (uint256 amountTokenOut)
+    {
         if (tokenOut == balLp) {
             amountTokenOut = amountSharesToRedeem;
         } else {
@@ -303,7 +342,11 @@ abstract contract PendleAuraBalancerStableLPSY is SYBaseWithRewards {
     function assetInfo()
         external
         view
-        returns (AssetType assetType, address assetAddress, uint8 assetDecimals)
+        returns (
+            AssetType assetType,
+            address assetAddress,
+            uint8 assetDecimals
+        )
     {
         return (AssetType.LIQUIDITY, balLp, IERC20Metadata(balLp).decimals());
     }
```

### contracts/core/libraries/Errors.sol
```diff
@@ -116,6 +116,8 @@ library Errors {
 
     error SYStargateRedeemCapExceeded(uint256 amountLpDesired, uint256 amountLpRedeemable);
 
+    error SYBalancerReentrancy();
+
     // Liquidity Mining
     error VCInactivePool(address pool);
     error VCPoolAlreadyActive(address pool);
```

### contracts/interfaces/Balancer/IVault.sol
```diff
@@ -5,6 +5,21 @@ import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
 import "./IAsset.sol";
 
 interface IVault {
+    enum UserBalanceOpKind {
+        DEPOSIT_INTERNAL,
+        WITHDRAW_INTERNAL,
+        TRANSFER_INTERNAL,
+        TRANSFER_EXTERNAL
+    }
+
+    struct UserBalanceOp {
+        UserBalanceOpKind kind;
+        IAsset asset;
+        uint256 amount;
+        address sender;
+        address payable recipient;
+    }
+
     struct JoinPoolRequest {
         address[] assets;
         uint256[] maxAmountsIn;
@@ -61,12 +76,14 @@ interface IVault {
         uint256 deadline
     ) external payable returns (uint256);
 
-    function getPoolTokens(
-        bytes32 poolId
-    )
+    function getPoolTokens(bytes32 poolId)
         external
         view
-        returns (IERC20[] memory tokens, uint256[] memory balances, uint256 lastChangeBlock);
+        returns (
+            IERC20[] memory tokens,
+            uint256[] memory balances,
+            uint256 lastChangeBlock
+        );
 
     function WETH() external view returns (IERC20);
 
```
