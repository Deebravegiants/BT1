# [M] Possible Costly Pool Tokens From Improper Initialization

## Summary
Severity: Medium
Contest weight: 0.4629
Dataset id: 12910
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Ribbon Finance protocol allows users to deposit supported assets and get in return rETH-THETA pool tokens to represent the pool share. While examining the share calculation with the given deposits, we notice an issue that may unnecessarily make the pool token, i.e., rETH-THETA, extremely expensive and bring hurdles (or even causes loss) for later depositors. To elaborate, we show below the deposit() routine. This routine is used for participating users to deposit the supported assets (e.g., WETH) and get respective pool tokens in return. The issue occurs when the pool is being initialized under the assumption that the current pool is empty.
```solidity
/**
 * @notice Mints the vault shares to the msg.sender
 * @param amount is the amount of asset deposited
 */
function _deposit(uint256 amount) private {
    uint256 totalWithDepositedAmount = totalBalance();
    require(totalWithDepositedAmount < cap, "Cap exceeded");
    // amount needs to be subtracted from totalBalance because it has already been
    // added to it from either IWETH.deposit and IERC20.safeTransferFrom
    uint256 total = totalWithDepositedAmount.sub(amount);
    // Following the pool share calculation from Alpha Homora: https://github.com/AlphaFinanceLab/alphahomora/blob/340653c8ac1e9b4f23d5b81e61307bf7d02a26e8/contracts/5/Bank.sol#L104
    uint256 share = total == 0 ? amount : amount.mul(totalSupply()).div(total);
    emit Deposit(msg.sender, amount, share);
    _mint(msg.sender, share);
}
```
Specifically, when the pool is being initialized (line 191), the share value directly takes the value of amount (line 192), which is manipulatable by the malicious actor. As this is the first deposit, the current total supply equals the calculated share = amount = 1 WEI. With that, the actor can further deposit a huge amount of WETH assets with the goal of making the pool token extremely expensive. An extremely expensive pool token can be very inconvenient to use as a small number of 1WEI may denote a large value. Furthermore, it can lead to precision issue in truncating the computed pool tokens for deposited assets. If truncated to be zero, the deposited assets are essentially considered dust and kept by the pool without returning any pool tokens. This is a known issue that has been mitigated in popular UniswapV2. When providing the initial liquidity to the contract (i.e. when totalSupply is 0), the liquidity provider must sacrifice 1000 LP tokens (by sending them to address(0)). By doing so, we can ensure the granularity of the LP tokens is always at least 1000 and the malicious actor is not the sole holder. This approach may bring an additional cost for the initial liquidity provider, but this cost is expected to be low and acceptable.

## Recommendation
Revise current execution logic of deposit() to defensively calculate the share amount when the pool is being initialized. An alternative solution is to ensure a guarded launch process that safeguards the first deposit to avoid being manipulated.
