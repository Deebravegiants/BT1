# [M] Possible Sandwich/MEV Attack For Reduced Returns

## Summary
Severity: Medium
Contest weight: 0.4550
Dataset id: 11929
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The DjinnAutoBuyer contract has a helper routine, i.e., buyTokenFromBnb(), that is designed to swap fee token DJINN by BNB. We show below the implementation of buyTokenFromBnb() routine from the DjinnAutoBuyer contract.
```solidity
function buyTokenFromBnb(
    address _outTarget
) external payable {
    uint256 _amountOutBusd = amountOut(lpWbnbBusd, true, msg.value, SWAP_PERMILLION_PCS2);
    uint256 _amountOutDjinn = amountOut(lpDjinnBusd, false, _amountOutBusd, SWAP_PERMILLION_PCS1);
    // execute swap and transfer djinn to sender
    IWETH(wbnbToken).deposit{value: msg.value}();
    IWETH(wbnbToken).transfer(lpWbnbBusd, msg.value);
    IUniswapPool(lpWbnbBusd).swap(0, _amountOutBusd, lpDjinnBusd, new bytes(0));
    IUniswapPool(lpDjinnBusd).swap(_amountOutDjinn, 0, _outTarget, new bytes(0));
    emit BoughtToken(_amountOutDjinn);
}
```
We notice the token swap is routed to pancakeSwap and the actual swap operation swap() does not specify any restriction (with amountOutMin=0) on possible slippage and is therefore vulnerable to possible front-running attacks, resulting in a smaller gain for this round of yielding.
Note that this is a common issue plaguing current AMM-based DEX solutions. Specifically, a large trade may be sandwiched by a preceding sell to reduce the market price, and a tailgating buy-back of the same amount plus the trade amount. Such sandwiching behavior unfortunately causes a loss and brings a smaller return as expected to the trading user because the swap rate is lowered by the preceding sell. As a mitigation, we may consider specifying the restriction on possible slippage caused by the trade or referencing the TWAP or time-weighted average price of UniswapV2. Nevertheless, we need to acknowledge that this is largely inherent to current blockchain infrastructure and there is still a need to continue the search efforts for an effective defense.

## Recommendation
Improve the above function by adding necessary slippage control with the user-specified amountOutMin.
