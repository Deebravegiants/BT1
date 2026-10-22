# [M] Incorrect fee calculation

## Summary
Severity: Medium
Contest weight: 0.4311
Dataset id: 10517
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ContinuosBondingERC20Token.buyTokens charges less fees for the case when tokensToReceive > maxTokenToReceive than for the common flow.
```solidity
function buyTokens(uint256 minExpectedAmount) external payable nonReentrant returns (uint256) {
    if (liquidityGoalReached()) revert LiquidityGoalReached();
    if (msg.value == 0) revert NeedToSendETH();
    uint256 ethAmount = msg.value;
    uint256 feeAmount = (ethAmount * buyFee) / PERCENTAGE_DENOMINATOR;
    uint256 remainingAmount = ethAmount - feeAmount;
    uint256 tokenReserveBalance = getReserve();
    uint256 maxTokenToReceive = tokenReserveBalance - (MAX_TOTAL_SUPPLY - availableTokenBalance);
    uint256 tokensToReceive = bondingCurve.calculatePurchaseReturn(remainingAmount, ethBalance, tokenReserveBalance, bytes(""));
    if (tokensToReceive < minExpectedAmount) revert InSufficientAmountReceived();
    uint256 ethReceivedAmount = remainingAmount;
    uint256 refund;
    if (tokensToReceive > maxTokenToReceive) {
        tokensToReceive = maxTokenToReceive;
        ethReceivedAmount = getOutputPrice(tokensToReceive, ethBalance, tokenReserveBalance);
        feeAmount = (ethReceivedAmount * buyFee) / PERCENTAGE_DENOMINATOR;
        if (msg.value < (feeAmount + ethReceivedAmount)) {
            revert InsufficientETH();
        }
        refund = msg.value - (feeAmount + ethReceivedAmount);
    }
```

## Recommendation
Consider using a different way for fee calculation when tokensToReceive > maxTokenToReceive: `feeAmount = ethReceivedAmount * PERCENTAGE_DENOMINATOR / (PERCENTAGE_DENOMINATOR - buyFee) - ethReceivedAmount;`
