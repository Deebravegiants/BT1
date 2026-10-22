# [H] Using an oracle for another collection can DoS the trading

## Summary
Severity: High
Contest weight: 0.6183
Dataset id: 16165
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The main functionality of the CircuitBreaker contract is to halt the trading when the percentageChange > haltPercentage. This check is inside the tripBreaker function and allows users to disable the trading of the NFTs:
```solidity
function tripBreaker() external {
    int currentValue;
    uint updatedAt;
    (,currentValue,,,updatedAt) = CO.latestRoundData();
    if(uint(percentageChange) > haltPercentage) {
        haltedDays[date] = true;
        emit BreakerTripped(uint(percentageChange), nftOracleAddress, date);
    }
}
```
The problem arises from the fact that the Chainlink Oracle for BAYC (Bored Ape Yacht Club) is used. The latestRoundData call will return the floor price of the BAYC collection which will be used to calculate the percentageChange. The two NFT collections are absolutely irrelevant and taking a look at the analytics proves that. For example, the BAYC floor price went from 24.47 ETH on October 1st to 27.97 ETH on October 2nd while the floor price of TradFiLines was stable at 0.8 ETH for the same period.
Another concern is that the floor price for the last 15 days of the TradFiLines is stable at 0.7 ETH while the floor price of BAYC is quite volatile, bouncing between 24 ETH and 27+ ETH.
This could lead to a scenario where the actual percentageChange is less than the haltPercentage but the movements of the floor price of the BAYC collection will allow users to call tripBreaker successfully.
This will DoS the protocol for at least a day. It could be even more problematic if the floor price is volatile (as we have seen in the past) and the trading is halted for consecutive days.

## Recommendation
As there is no oracle for the TradFiLines collection floor price, there is no easy solution to this issue.
Consider removing the function to disable the trading or implement require checks which are not dependent on irrelevant external factors.
