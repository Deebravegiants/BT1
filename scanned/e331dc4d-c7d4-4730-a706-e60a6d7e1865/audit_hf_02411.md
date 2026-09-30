# [H] Several Business Logic Errors in PositionStorage::liquidatePosition()

## Summary
Severity: High
Contest weight: 0.7852
Dataset id: 12978
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the SatoshiSwap protocol, the PositionStorage contract also provides a helper routine, liquidatePosition(), to trigger the liquidation in case of the liquidation margin is reached. To elaborate, we show below the related code snippet.
```solidity
function liquidatePosition() external marginPoolOnly returns (PositionLibrary.SuccessLiquidatePosition memory output) {
    //The detailed implementation removed per the request from the team
}
```
While analyzing this routine, we notice there are several logic errors. The first one is when this routine refers the Oracle to get the price of position.quoteToken based on position.baseToken. And there is a call of SatoshiLibrary.sortTokens() with the input arguments of position.quoteToken and position.baseToken. The return values tokenPair1 and tokenPair2 are passed as the input arguments for ISatoshiOracle(oracle).getPrice(). The assumptions of tokenPair1 == position.quoteToken and tokenPair2 == position.baseToken are not necessarily guaranteed and may be violated if position.baseToken < position.quoteToke. The second one is when this routine evaluates whether the liquidation amount is reached by checking position.ownedAmount.add(position.userAmount).mul(liquidateMargin()).div(denominator()) >= outputAmount. The liquidateMargin()).div(denominator() is directly taken into the multiplication with position.ownedAmount.add(position.userAmount), and compared with outputAmount. However, according to the documentation, the logic here should be the opposite way, which takes the (denominator()-liquidateMargin()).div(denominator()) to multiply with position.ownedAmount.add(position.userAmount). The third one is the poolInterestAmount calculation from position.ownedAmount > outputAmount. There is a logic error because when outputAmount is smaller than position.ownedAmount, there is no interest from this operation, which means the output.poolInterestAmount should be 0. However, the current implementation is taking the opposite way. Also, even if we change the if condition to the opposite way, the calculation of output.poolInterestAmount has another logic error where the position.ownedAmount.sub(outputAmount) will always revert as the position.ownedAmount is supposed to be smaller than the outputAmount. The fourth one is the storedBalance calculation from storedBalance.sub(output.outputAmount.sub(output.ownedAmount)). There is a logic error because when poolInterestAmount is not larger than 0, it means there is a loss from the positionStorage::liquidatePosition(). In this case, the calculation of output.outputAmount.sub(output.ownedAmount) will revert as output.outputAmount is supposed to be smaller than output.ownedAmount.
```solidity
function liquidatePosition(uint256 _positionId, uint256 _slippage) returns (bool success, uint256 reward) {
    //The detailed implementation removed per the request from the team
}
```

## Recommendation
Correct the logic error mentioned above accordingly.
