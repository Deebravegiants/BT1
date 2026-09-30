# [H] Insufficient Chainlink price feed validation

## Summary
Severity: High
Contest weight: 0.3099
Dataset id: 10116
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In ChainlinkLPOracleGMU there are multiple problems with the Chainlink price feed input validation. The _getCurrentChainlinkResponse method calls the Chainlink price feed aggregator's latestRoundData method, but it does no input validation on it - the answer is not checked if it is actually a positive number and also the timestamp or updatedAt property is also not checked if it isn't too old. Another problem is the try-catch approach, where the cached ChainlinkResponse object has a success field that holds if the call to the aggregator failed or succeeded. This value is properly set, but not actually used anywhere, meaning in the other methods it is possible that the ChainlinkResponse objects that others operate with has a success = false property, but is still used as the response is valid. https://docs.chain.link/docs/historical-price-data/#historical-rounds https://docs.chain.link/docs/faq/#how-can-i-check-if-the-answer-to-a-round-is-being-carried-over-from-a-previous-round The final issue here is that one of the chains the contract will be deployed on is the Arbitrum chain, where the Chainlink feeds have special properties. They operate with a sequencer, which mandatorily has to be checked if it is up and if it isn't the transaction should revert or set success = false, otherwise the protocol might operate with a stale/invalid price.

## Recommendation
Instead of using try-catch just revert on failed external calls to the Chainlink aggregator, since there is no clean way to continue from a failed message. When it comes to the Arbitrum sequencer validation, follow the guide in Chainlink's L2 sequencer feeds docs. For the input of latestRoundData make sure to validate the input values returned from the call properly.
