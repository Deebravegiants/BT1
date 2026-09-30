# [M] Unsafe Minout Parameter in CRVExchange::handleExtraToken()

## Summary
Severity: Medium
Contest weight: 0.4488
Dataset id: 11987
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As we introduced in Section 3.1, the IUSDCPoolBase::earn_crv() function swaps the CRV earned to target token by calling CRVExchange::handleExtraToken(). The latter loops through the DEXs and ﬁnds out the one with best output. Then the function calls the DEX's swapExactTokensForTokens() to sell the earned CRV. The amountOutMin parameter of swapExactTokensForTokens() is the minimum amount of output tokens that must be received for the transaction not to revert.
```solidity
function handleExtraToken(address from, address target_token, uint256 amount) public {
    uint256 maxOut = 0;
    uint256 fdi = 0;
    uint256 fpi = 0;
    for (uint di = 0; di < dexs.length; di++){
        for (uint pi = 0; pi < path_indexes.length; pi++){
            if (path_from_addr(pi) != from || path_to_addr(pi) != target_token) {
                continue;
            }
            uint256 t = get_out_for_dex_path(di, pi, amount);
            if (t > maxOut) {
                fdi = di;
                fpi = pi;
                maxOut = t;
            }
        }
    }
    IERC20(from).transferFrom(msg.sender, address(this), amount);
    IERC20(from).approve(dexs[fdi], amount);
    SushiUniInterface(dexs[fdi]).swapExactTokensForTokens(amount, 0, paths[path_indexes[fpi]], address(this), block.timestamp + 10800);
    uint256 target_amount = IERC20(target_token).balanceOf(address(this));
    IERC20(target_token).approve(address(msg.sender), target_amount);
    CFControllerInterface(msg.sender).refundTarget(target_amount);
}
```
However, the amountOutMin here is set to 0. The front runners can buy the target token and sell the tokens after the admin have called the IUSDCPoolBase::earn_crv(). Since the amountOutMin is 0, the transaction harvesting the CRV won't revert if the output is small.

## Recommendation
Calculate the amountOutMin and submit it as a parameter.
