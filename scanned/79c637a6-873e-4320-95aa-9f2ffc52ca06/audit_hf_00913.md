# [H] Malicious request with `amount == 0` can be used to drain market

## Summary
Severity: High
Contest weight: 0.7852
Dataset id: 2731
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
{
    BetState storage betState = bets[requestCommitment]; 
    BetCommitment betCommitment = getCommitment(betBlob); 
    require( 
        request.betCommitment == betCommitment, 
        MarketsInvalidBetRequest(requestCommitment, betCommitment, request.betCommitment) 
    ); 
    require(betState.amount == request.amount, MarketsBetDoesntExist(requestCommitment)); 

    // Since the bet is revealed, no amount should remain to be revealed 
    betState.amount = 0; 
}
```

When revealing a bet, the above lines are designed to prevent invalid bets from being revealed. By checking that `betState.amount == request.amount` then setting `betState.amount` to `0`, it simultaneously prevents most invalid bets as well as double reveals. However, it misses the edge case in which `request.amount == 0`. This allows a malicious user to submit an invalid `betRequest` with `request.amount == 0` and a corresponding `betBlob` that will successfully bypass this check.  

```solidity
function _getPayout( 
    MarketBlob calldata marketBlob, 
    ResultBlob calldata resultBlob, 
    BetRequest calldata request, 
    BetBlob calldata betBlob 
) 
    internal 
    pure 
    override 
    returns (uint256 winningPotAmount, uint256 losingPotAmount, uint256 marketDeadlineBlock, address creator) 
{ 
    MarketInfo memory marketInfo = abi.decode(marketBlob.data, (MarketInfo)); 
    BetHiddenInfo memory hiddenInfo = abi.decode(betBlob.data, (BetHiddenInfo)); 
    ResultInfo memory resultInfo = abi.decode(resultBlob.data, (ResultInfo)); 

    marketDeadlineBlock = marketInfo.deadlineBlock; 

    creator = abi.decode(marketBlob.data, (MarketInfo)).creator; 
    uint256 betOutcomeMask = (1 << hiddenInfo.outcome); 
    if ((betOutcomeMask & resultInfo.winningOutcomeMask) != 0) { 
        winningPotAmount = request.amount; 
        losingPotAmount = 
            Math.mulDiv(hiddenInfo.betWeight, resultInfo.losingTotalPot, resultInfo.winningTotalWeight); 
    } 
}
```

Since the `betBlob` is arbitrary, any value for `hiddenInfo.betWeight` can be supplied. As a result, the entire `resultInfo.losingTotalPot` can be stolen via this attack vector.

## Recommendation
`revealBet` should revert if `request.amount == 0`.
