# [M] OCL_ZVE::pushToLockerMulti() will revert due to allowance not being zero

## Summary
Severity: Medium
Contest weight: 0.6061
Dataset id: 22707
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
OCL_ZVE::pushToLockerMulti() verifies that the allowances for both tokens is 0 after providing liquidity to UniswapV2 or Sushi routers, however there is a high likelihood that one allowance will not be 0, due to setting a 90% minimum liquidity provided value. Therefore, the function will revert most of the time breaking core functionality of the locker, making the contract useless. The DAO can add liquidity to UniswapV2 or Sushi through OCL_ZVE::pushToLockerMulti() function, where addLiquidity is called on router:

```solidity
OCL_ZVE.sol#L198C78-L198
IRouter_OCL_ZVE(router).addLiquidity(
OCL_ZVE.sol#L90
address public immutable router;
/// @dev Address for the Router (Uniswap v2 or Sushi).
```

The router is intended to be Uniswap v2 or Sushi (Sushi router uses the same code as Uniswap v2 0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f). UniswapV2Router02::addLiquidity

```solidity
function addLiquidity(
address tokenA,
address tokenB,
uint amountADesired,
uint amountAMin,
uint amountBMin,
address to,
uint deadline
) external virtual override ensure(deadline) returns (uint amountA, uint amountB, uint liquidity) {
(amountA, amountB) = _addLiquidity(tokenA, tokenB, amountADesired, amountAMin, amountBMin);
address pair = UniswapV2Library.pairFor(factory, tokenA, tokenB);
TransferHelper.safeTransferFrom(tokenA, msg.sender, pair, amountA);
TransferHelper.safeTransferFrom(tokenB, msg.sender, pair, amountB);
liquidity = IUniswapV2Pair(pair).mint(to);
}
```

When calling the function 4 variables relevant to this issue are passed: deposit, whilst amountAMin and amountBMin are the minimum amounts of tokens we want to deposit. Meaning the true amount that will deposit be deposited for each token will be inbetween those 2 values, e.g: amountAMin <= amountA <= amountADesired. Where amountA is how much of tokenA will be transfered. The transfered amount are amountA and amountB which are calculated as follows: UniswapV2Router02::_addLiquidity

```solidity
function _addLiquidity(
address tokenA,
address tokenB,
uint amountADesired,
uint amountAMin,
uint amountBMin
) internal virtual returns (uint amountA, uint amountB) {
// create the pair if it doesn't exist yet
if (IUniswapV2Factory(factory).getPair(tokenA, tokenB) == address(0)) {
IUniswapV2Factory(factory).createPair(tokenA, tokenB);
}
(uint reserveA, uint reserveB) = UniswapV2Library.getReserves(factory, tokenA, tokenB);
if (reserveA == 0 && reserveB == 0) {
(amountA, amountB) = (amountADesired, amountBDesired);
} else {
uint amountBOptimal = UniswapV2Library.quote(amountADesired, reserveA, reserveB);
require(amountBOptimal >= amountBMin, 'UniswapV2Router: INSUFFICIENT_B_AMOUNT');
(amountA, amountB) = (amountADesired, amountBOptimal);
}
uint amountAOptimal = UniswapV2Library.quote(amountBDesired, reserveB, reserveA);
assert(amountAOptimal <= amountADesired);
require(amountAOptimal >= amountAMin, 'UniswapV2Router: INSUFFICIENT_A_AMOUNT');
(amountA, amountB) = (amountAOptimal, amountBDesired);
}
```

UniswapV2Router02::_addLiquidity receives a quote for how much of each token can be added and validates that the values fall within the amountAMin and amountADesired range. Unless the exactly correct amounts are passed as desired, the deposited amount will be less than the desired amount. Now lets look at how OCL_ZVE interacts with the Uniswapv2 router:

```solidity
OCL_ZVE::addLiquidity
// Router addLiquidity() endpoint.
uint balPairAsset = IERC20(pairAsset).balanceOf(address(this));
uint balZVE = IERC20(ZVE).balanceOf(address(this));
IERC20(pairAsset).safeIncreaseAllowance(router, balPairAsset);
IERC20(ZVE).safeIncreaseAllowance(router, balZVE);
// Prevent volatility of greater than 10% in pool relative to amounts present.
(uint256 depositedPairAsset, uint256 depositedZVE, uint256 minted) =
IRouter_OCL_ZVE(router).addLiquidity(
pairAsset,
ZVE,
balPairAsset,
balZVE,
(balPairAsset * 9) / 10,
(balZVE * 9) / 10,
address(this), block.timestamp + 14 days
);
emit LiquidityTokensMinted(minted, depositedZVE, depositedPairAsset);
assert(IERC20(pairAsset).allowance(address(this), router) == 0);
assert(IERC20(ZVE).allowance(address(this), router) == 0);
```

The function first increases the allowances for both tokens to balPairAsset and balZVE respectively. When calling the router, balPairAsset and valZVE are provided as the desired amount of liquidity to add, however (balPairAsset * 9) / 10 and (balZVE * 9) / 10 are also passed as minimums for how much liquidity we want to add. balPairAsset therefore the allowance after providing liquidity will be: 0 <= IERC20(pairAsset).allowance(address(this), router) <= balPairAsset - (balPairAsset * 9) / 10 however the function expects the allowance to be 0 for both tokens after providing liquidity. The same applies to the ZVE allowance. This means that in most cases one of the assert statements will not be met, leading to the add liquidity call to revert. This is unintended behaviour, as the function passed a 90% minimum amount, however the allowance asserts do not take this into consideration. Calls to OCL_ZVE::pushToLockerMulti() will revert a majority of the time, causing core functionality of providing liquidity through the locker to be broken.

## Recommendation
The project wants to clear allowances after all transfers, therefore set the router allowance to 0 after providing liquidity using the returned value from the router:

```diff
(uint256 depositedPairAsset, uint256 depositedZVE, uint256 minted) =
IRouter_OCL_ZVE(router).addLiquidity(
pairAsset,
ZVE,
balPairAsset,
balZVE,
(balPairAsset * 9) / 10,
(balZVE * 9) / 10,
address(this), block.timestamp + 14 days
);
emit LiquidityTokensMinted(minted, depositedZVE, depositedPairAsset);
- assert(IERC20(pairAsset).allowance(address(this), router) == 0);
- assert(IERC20(ZVE).allowance(address(this), router) == 0);
+ uint256 pairAssetAllowanceLeft = balPairAsset - depositedPairAsset;
+ if (pairAssetAllowanceLeft > 0) {
+ IERC20(pairAsset).safeDecreaseAllowance(router, pairAssetAllowanceLeft);
+ }
+ uint256 zveAllowanceLeft = balZVE - depositedZVE;
+ if (zveAllowanceLeft > 0) {
+ IERC20(ZVE).safeDecreaseAllowance(router, zveAllowanceLeft);
+ }
```

This will remove the left over allowance after providing liquidity, ensuring the allowance is 0.
