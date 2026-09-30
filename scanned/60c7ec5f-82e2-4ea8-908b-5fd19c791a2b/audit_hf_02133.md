# [M] Possible Sandwich/MEV For Maximum PlatformTokenDivs

## Summary
Severity: Medium
Contest weight: 0.4603
Dataset id: 11976
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
As mentioned in Section 3.1, the DYP Earn Vault has a built-in integration with Compound to earn
interests. Also, when a user withdraws from the protocol, there is an associated withdrawal fee,
which is partially used to buy back the protocol token in order to add liquidity and maintain the
token price stability. In the following, we examine the platform token dividends that may be claimed
by participating users.
To elaborate, we show below the full implementation of the _claimPlatformTokenDivs() routine.
This routine firstly retrieves the current dividend balance of the requesting user (in the deposited
tokens - line 1125), then queries Uniswap for possible converted amount in the platform tokens (line
1135), and finally transfers out the queried amount (line 1137).
function _claimPlatformTokenDivs() private {
    updateAccount(msg.sender);
    uint amount = platformTokenDivsBalance[msg.sender];
    platformTokenDivsBalance[msg.sender] = 0;
    if (amount == 0) return;
    address[] memory path = new address[](3);
    path[0] = TRUSTED_DEPOSIT_TOKEN_ADDRESS;
    path[1] = uniswapRouterV2.WETH();
    path[2] = TRUSTED_PLATFORM_TOKEN_ADDRESS;
    uint estimatedAmountOut = uniswapRouterV2.getAmountsOut(amount, path)[2];
    decreaseTokenBalance(TRUSTED_PLATFORM_TOKEN_ADDRESS, estimatedAmountOut);
    IERC20(TRUSTED_PLATFORM_TOKEN_ADDRESS).safeTransfer(msg.sender, estimatedAmountOut);
    totalEarnedPlatformTokenDivs[msg.sender] = totalEarnedPlatformTokenDivs[msg.sender].add(estimatedAmountOut);
    emit PlatformTokenRewardClaimed(msg.sender, estimatedAmountOut);
}
```
We notice the collected dividends are (virtually) routed to UniswapV2 in order to swap them to
the platform token as dividends. And the getAmountsOut() calculation does not have any restriction
on possible slippage and is therefore vulnerable to possible sandwich attacks, resulting in a smaller
gain for this round of yielding. Note that both Vault and VaultWETH contracts share the same issue.
We need to admit that this is a common issue plaguing current AMM-based DEX solutions.
Specifically, a large trade may be sandwiched by a preceding sell to reduce the market price, and
a tailgating buy-back of the same amount plus the trade amount.
Such sandwiching behavior
unfortunately causes a loss and brings a smaller return as expected to the trading user or the claiming
user in our case because the (virtual) swap rate is lowered by the preceding sell. As a mitigation, we
may consider specifying the restriction on possible slippage caused by the trade or referencing the
TWAP or time-weighted average price of UniswapV2. Nevertheless, we need to acknowledge that this is
largely inherent to current blockchain infrastructure and there is still a need to continue the search
efforts for an effective defense.

## Recommendation
Develop an effective mitigation to the above front-running attack to better protect the interests of farming users.
