# [H] Uniswap and 1inch swap function in Zapper send wrong tokenMinimum

## Summary
Severity: High
Contest weight: 0.7633
Dataset id: 22758
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The swapFrom1inchUnoswapAndBond and swapFromUniswapAndBond function in zapper incorrectly send the output WETH amount as the tokenMinimum in FSD.bondTo when it should be the minimum amount of FSD tokens to mint. Notice the following swapFrom1inchUnoswapAndBond and swapFromUniswapAndBond ontractsV2/contracts/zap/Zapper.sol#L66
```solidity
function swapFromUniswapAndBond(
) public returns (bool) {
    uint256 amountIn = ISwapRouter(UNISWAP_V3_ROUTER).exactInputSingle(params);
    FSD.bondTo(to, amountIn);
}

function swapFrom1inchUnoswapAndBond(
) public returns (bool) {
    uint256 swappedAmount = IOneInchRouter(oneInchDexRouter).unoswapTo(address(this), srcToken, amount, minReturn, pools);
    FSD.bondTo(to, swappedAmount);
}
```
Notice how both take the output amount and pass it along to FDS.bondTo as the second parameter. However, FDS.bondTo expects to receive the minimum amount of FSD tokens to mint (slippage protection):
```solidity
* @param tokenMinimum The minimum amount of tokens to be minted
function bondTo(address to, uint256 tokenMinimum) external payable override {
    return _bondInternal(to, tokenMinimum, true);
}
```
Impact is dependent of FSD price and bond amount:
1. If bonding amount is smaller then minted FSD - user could have lost tokens due to slippage (can be abused by MEV bots)
2. If bonding amount is larger then minted FSD - function will revert

## Recommendation
Consider allowing the user to supply the FSD slippage to the swap function. Then send the user supplied slippage to the bondTo function
