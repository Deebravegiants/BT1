# [M] V2AMO and V3AMO: USDT Ap-

## Summary
Severity: Medium
Contest weight: 0.5918
Dataset id: 2630
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As the documentation mentions, the contracts are designed to be compatible with any EVM chain and support USDT: USD is a generic name for a reference stable coin paired with BOOST in the AMO ( USDC and USDT are the first natural candidates ) However, both the V2AMO and V3AMO contracts will not work with USDT, as they will revert during the _addLiquidity() and _unfarmBuyBurn() functions. Both V2AMO and V3AMO use OpenZeppelin's IERC20Upgradeable interface, which expects a boolean return value when calling the approve() function. However, USDT’s implementation of the approve() function does not return a boolean value, which causes the contract to revert during execution.
```solidity
/**
 * @dev Approve the passed address to spend the specified amount of tokens on behalf of msg.sender.
 * @param _spender The address which will spend the funds.
 * @param _value The amount of tokens to be spent.
 */
function approve(address _spender, uint _value) public onlyPayloadSize(2 * 32) {
```
The functions _addLiquidity() and _unfarmBuyBurn() in both contracts expect a boolean return value, causing them to revert when interacting with USDT. example V3AMO::_addLiquidity and V3AMO::_unfarmBuyBurn:
```solidity
function _addLiquidity(uint256 usdAmount, uint256 minBoostSpend, uint256 minUsdSpend, uint256 deadline)
    internal
    override
    returns (uint256 boostSpent, uint256 usdSpent, uint256 liquidity)
{
    // Approve the transfer of BOOST and USD tokens to the pool
    IERC20Upgradeable(boost).approve(pool, boostAmount);
    IERC20Upgradeable(usd).approve(pool, usdAmount);
    (uint256 amount0Min, uint256 amount1Min) = sortAmounts(minBoostSpend, minUsdSpend);
    uint128 currentLiquidity = IV3Pool(pool).liquidity();
    liquidity = (usdAmount * currentLiquidity) / IERC20Upgradeable(usd).balanceOf(pool);
    // Add liquidity to the BOOST-USD pool within the specified tick range
    (uint256 amount0, uint256 amount1) = IV3Pool(pool).mint(
        address(this), tickLower, tickUpper, uint128(liquidity), amount0Min, amount1Min, deadline
    );
    // Revoke approval from the pool
    IERC20Upgradeable(boost).approve(pool, 0);
    IERC20Upgradeable(usd).approve(pool, 0);
}

function _unfarmBuyBurn(
    uint256 liquidity,
    uint256 minBoostRemove,
    uint256 minUsdRemove,
    uint256 minBoostAmountOut,
    uint256 deadline
)
internal
override
returns (uint256 boostRemoved, uint256 usdRemoved, uint256 usdAmountIn, uint256 boostAmountOut)
{
    // Approve the transfer of usd tokens to the pool
    IERC20Upgradeable(usd).approve(pool, usdRemoved);
    // Execute the swap and store the amounts of tokens involved
    (int256 amount0, int256 amount1) = IV3Pool(pool).swap(
        address(this),
        boost > usd, // Determines if we are swapping USD for BOOST (true) or BOOST for USD (false)
        int256(usdRemoved),
        targetSqrtPriceX96,
        minBoostAmountOut,
        deadline
    );
    // Revoke approval from the pool
    IERC20Upgradeable(usd).approve(pool, 0);
    //...
}
```
V2AMO::_addLiquidity and V2AMO::_unfarmBuyBurn faces the same issue Internal pre-conditions External pre-conditions Attack Path Adding liquidity and farming will fail due to a revert on USDT approvals

## Recommendation
Use safeApprove instead of approve
