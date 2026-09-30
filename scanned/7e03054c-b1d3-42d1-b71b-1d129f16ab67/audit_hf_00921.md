# [M] No Slippage Protection in buyWithReferral

## Summary
Severity: Medium
Contest weight: 0.4325
Dataset id: 2766
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When users buy tokens using the buyWithReferral function, they specify the token amount to buy and send the corresponding amount of ETH. There isn’t slippage protection due to the assumption that the maximum price users will pay is tokenAmountToBuy/msg.value, allowing users to control the price they However, users can still end up paying a higher price than expected (slippage) because: The number of tokens available for purchase might be less than the tokenAmountToBuy if the remaining token supply is less than the tokenAmountToBuy. As the available token supply decreases, the price of the token increases. In a scenario where a user intends to buy 10e18 tokens with 1 ETH (price is 0.1 ETH per 1e18 tokens), but another user front-runs and buys 9e18 tokens before them, the initial user will only receive 1e18 tokens and end up paying more than 0.1 ETH, which is more than the intended price of 0.1 ETH per 1e18 tokens.
```solidity
function buyWithReferral(
    address erc20Address,
    uint256 tokenAmountToBuy,
    address referral
) public
    payable
    nonReentrant
    validToken(erc20Address)
{
    uint256 tokenAmountLeft = getTokenAmountLeft(erc20Address);
    // (tokenAmountToBuy >= tokenAmountLeft) { // @audit amount to buy can be less
    tokenAmountToBuy = tokenAmountLeft;
    // pause the curve when all available tokens have been bought
    curves[erc20Address].isPaused = true;
    emit BondingCurveCompleted(erc20Address);
}
```

## Recommendation
Allow users to specify the minimum amount of tokens they will receive to avoid slippage.
