# [M] WithdrawPeriphery#_convertToToken slippage

## Summary
Severity: Medium
Contest weight: 0.5925
Dataset id: 17762
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
WithdrawPeriphery allows the user to redeem junior share vaults to any token available on GMX. To prevent users from losing large amounts of value to MEV the contract applies slippage protection based on a percentage of the estimated out value. The amount of the output is denominated in USDC so _convertToToken always returns the number of tokens to 6 decimals. This works fine for USDC but for other tokens like WETH or WBTC that are 18 decimals the slippage protection is completely ineffective and can lead to loss of funds for users that are withdrawing.
```solidity
function _convertToToken(address token, address receiver) internal returns (uint256 amountOut) {
    // this value should be whatever glp is received by calling withdraw/redeem to junior vault
    uint256 outputGlp = fsGlp.balanceOf(address(this));
    // using min price of glp because giving in glp
    uint256 glpPrice = _getGlpPrice(false);
    // using max price of token because taking token out of gmx
    uint256 tokenPrice = gmxVault.getMaxPrice(token);
    // apply slippage threshold on top of estimated output amount
    uint256 minTokenOut = outputGlp.mulDiv(glpPrice * (MAX_BPS - slippageThreshold), tokenPrice * MAX_BPS);
    // will revert if atleast minTokenOut is not received
    amountOut = rewardRouter.unstakeAndRedeemGlp(address(token), outputGlp, minTokenOut, receiver);
}
```
WithdrawPeriphery allows the user to redeem junior share vaults to any token available on GMX. To prevent users from losing large amounts of value to MEV the contract applies slippage protection based on a percentage of the estimated out value. The slippage protection assumes that the output token decimals is 6, but this is not true for most tokens on GMX. This leads to minimal slippage protection for tokens with more than 6 decimals. Users withdrawing tokens other than USDC can suffer huge loss of funds due to virtually no slippage protection

## Recommendation
Adjust minTokenOut to match the decimals of the token:
```solidity
uint256 minTokenOut = outputGlp.mulDiv(glpPrice * (MAX_BPS - slippageThreshold), tokenPrice * MAX_BPS);
minTokenOut = minTokenOut * 10 ** (token.decimals() - 6);
```
