# [M] prevLastOutBalance/prevSwapEthBalance should

## Summary
Severity: Medium
Contest weight: 0.5942
Dataset id: 22805
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
in takeTokensAndTrade() we would record prevLastOutBalance and lastOutBalance
Then limit lastOutBalance - prevLastOutBalance >= minAmountOut But when the inputToken and the outputToken are both eth , prevLastOutBalance without subtract msg.value, resulting in the difference being less than minAmountOut
in Maradona.takeTokensAndTrade() At the beginning of the trade we record prevLastOutBalance
```solidity
function takeTokensAndTrade(
    ...
    uint256 prevLastOutBalance = 0;
    uint256 minAmountOut = 0;
    if (swapOps.length > 0) {
        minAmountOut = swapOps[swapOps.length - 1].minAmountOut;
        swapOps[swapOps.length - 1].minAmountOut = 1;
        bool isToEth = swapOps[swapOps.length - 1].outputToken == address(0);
        if (isToEth) {
            prevLastOutBalance = address(this).balance;
        }
    }
```
After the swap we check the minAmountOut
```solidity
// We recover last swapOp output
uint256 lastOutBalance = 0;
if (swapOps.length > 0) {
    bool isToEth = swapOps[swapOps.length - 1].outputToken == address(0);
    if (isToEth) {
        lastOutBalance = address(this).balance;
    } else {
        IERC20 lastOutputToken = IERC20(swapOps[swapOps.length - 1].outputToken);
        lastOutBalance = lastOutputToken.balanceOf(address(this));
    }
}
require(lastOutBalance - prevLastOutBalance >= minAmountOut, "Maradona: last output amount is less than minAmountOut");
```
// End of (2)
prevLastOutBalance contains msg.value If isToEth==true will cause minAmountOut check to fail
For example the following common MEV arbitrage, inputToken = outputToken = eth
ops[0] = {inputToken = eth , amountIn = 1000, outputToken = usdc , market=uniswap 2} ops[1] = {inputToken = usdc, outputToken = ... market=uniswap 3 } ... ops[x] = {inputToken = ... , outputToken = eth ,minAmountOut = 1010 }
//«----last outputToken == eth
Calculate the result: prevLastOutBalance = 1000 lastOutBalance = 1010
lastOutBalance - prevLastOutBalance = 10 will fail the minAmountOut=1010 check!
minAmountOut check fails, takeTokensAndTrade() will not work properly

## Recommendation
if ops[0].inputToken == ops[last].outputToken Maradona.sol : prevLastOutBalance needs to subtract msg.value Messi.sol : prevLastOutBalance needs to subtract claimedAmount
