# [M] No minAnswer/maxAnswerCircuit Breaker Checks

## Summary
Severity: Medium
Contest weight: 0.4614
Dataset id: 20120
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Oracle.sol contract, while currently applying a safety check (this can be side stepped, check my other submission ) to ensure returned prices are greater than zero, which is commendable, as it effectively mitigates the risk of using negative prices, there should be an implementation to ensure the returned prices are not at the extreme boundaries (minAnswer and maxAnswer). Without such a mechanism, the contract could operate based on incorrect prices, which could lead to an over- or under-representation of the asset's value, potentially causing significant harm to the protocol.  
Vulnerability Details  
Chainlink aggregators have a built in circuit breaker if the price of an asset goes outside of a predetermined price band. The result is that if an asset experiences a huge drop in value (i.e. LUNA crash) the price of the oracle will continue to return the minPrice instead of the actual price of the asset. This would allow user to continue borrowing with the asset but at the wrong price. This is exactly what happened to Venus on BSC when LUNA imploded. In its current form, the getUnderlyingPrice() function within the Oracle.sol contract retrieves the latest round data from Chainlink, if the asset's market price plummets below minAnswer or skyrockets above maxAnswer, the returned price will still be minAnswer or maxAnswer, respectively, rather than the actual market price. This could potentially lead to an exploitation scenario where the protocol interacts with the asset using incorrect price information.  
Take a look at Oracle.sol#L106-L123:  
```solidity
function getLatestRoundData(AggregatorV3Interface _aggregator)
    internal
    view
    returns (
        uint80,
        uint256 finalPrice,
        uint256
    )
{
    (uint80 round, int256 latestPrice, , uint256 latestTimestamp, ) =
    _aggregator.latestRoundData();

    finalPrice = uint256(latestPrice);
    if (latestPrice <= 0) {
        requireEnoughHistory(round);
        (round, finalPrice, latestTimestamp) = getRoundData(_aggregator, round - 1);
    }
    return (round, finalPrice, latestTimestamp);
}
```
Illustration:  
• Present price of TokenA is $10  
• TokenA has a minimum price set at $1 on chainlink  
• The actual price of TokenA dips to $0.10  
Consequently, users can interact with protocol using TokenA as though it were still valued at $1, which is a tenfold overestimate of its real market value.  
The potential for misuse arises when the actual price of an asset drastically changes but the oracle continues to operate using the minAnswer or maxAnswer as the asset's price. In the case of it going under the minAnswer malicious actors obviously have the upperhand and could give their potential going to zero worth tokens to protocol

## Recommendation
Since there is going to be a whitelist of tokens to be added, the minPrice/maxPrice could be checked and a revert could be made when this is returned by chainlink or case
