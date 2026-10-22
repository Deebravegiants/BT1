# [H] Any bet can be refunded by supplying invalid `betBlob`

## Summary
Severity: High
Contest weight: 0.6184
Dataset id: 2730
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function requestRefund(BetRequest calldata request, BetBlob calldata betBlob) 
    external 
    returns (IERC20 token, address to, uint256 amount) 
{
    RequestCommitment requestCommitment = getCommitment(request); 
    BetState storage betState = bets[requestCommitment]; 
    require(betState.amount == request.amount, MarketsBetDoesntExist(requestCommitment)); 
    betState.amount = 0; 

    require( 
        block.number >= request.refundStartBlock, 
        MarketsRefundTooEarly(requestCommitment, request.refundStartBlock, block.number) 
    ); 

    MarketCommitment marketCommitment = _getMarketFromBet(betBlob); 
    ResultCommitment resultCommitment = marketResults[marketCommitment]; 
    require( 
        resultCommitment == nullResultCommitment, MarketsResultAlreadyRevealed(marketCommitment, resultCommitment) 
    ); 

    token = request.token; 
    to = request.from; 
    amount = request.amount; 

    token.safeTransfer(to, amount); 

    emit MarketsRefundIssued(requestCommitment, marketCommitment, token, to, amount); 
}
```

When requesting a refund, the `marketCommitment` is retrieved from the `betBlob` data. However the commitment hash of the supplied `betBlob` is never validated against the `BetCommitment` stored in the `betRequest`. This allows any arbitrary `betBlob` to be supplied during the refund process. To exploit this, a malicious user can supply a `betBlob` that links to an invalid market. This satisfies the `resultCommitment == nullResultCommitment` requirement, allowing users to receive an invalid refund and cause a shortfall in the protocol.

## Recommendation
The commitment hash of the supplied `betBlob` should be validated against the `BetCommitment` in the `betRequest`. This ensures that the `betBlob` corresponds to the originally committed `BetCommitment`, preventing the use of arbitrary or malicious `betBlob` data during refund requests.
