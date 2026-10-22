# [M] Potential DOS attack due to large computation in `getAuctionData` function

## Summary
Severity: Medium
Reporter: 0x4non
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L202-L205
Type: audit-issue

## Details
# Potential DOS attack due to large computation in `getAuctionData` function

## Summary

The `getAuctionData` function on `MeritDutchAuction`, could potentially lead to a Denial-of-Service (DOS) attack. If the time duration of the auction (endTime - startTime) is very large, and the `stepSize` is quite small, it may lead to the creation of excessively large arrays, thereby leading to gas limitations, block gas limit issues, and potentially a DOS attack.

## Vulnerability Detail

In the provided code snippet, we can observe that two arrays, `priceSteps` and `priceStepTimestamps`, are instantiated with a size that depends on `(endTime - startTime) / stepSize + 1`. In a scenario where the auction duration is very large and the step size is very small, this calculation could result in the creation of enormous arrays. Consequently, the for-loop that populates these arrays will perform a huge number of iterations, potentially leading to gas limit issues, and hence, a denial of service.

## Impact

The impact is that the `getAuctionData` function could become uncallable if the arrays become too large due to the aforementioned issue. This would prevent users and potentially other contract functions from retrieving important auction data, which could disrupt the entire functionality of the contract.

## Code Snippet
[MeritDutchAuction.sol#L202-L205](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L202-L205)
```solidity
uint256[] memory priceSteps = new uint256[]((endTime - startTime) / stepSize + 1);
uint256[] memory priceStepTimestamps = new uint256[]((endTime - startTime) / stepSize + 1);

for(uint256 i = 0; i < priceSteps.length; i++) {
    priceStepTimestamps[i] = startTime + i * stepSize;
    priceSteps[i] = getPriceAt(priceStepTimestamps[i]);
}
```

## Tool used

Manual Review

## Recommendation

Consider limiting the size of `priceSteps` and `priceStepTimestamps` to a reasonable maximum to avoid potential DOS attack vectors. Another approach could be to calculate the price steps and timestamps dynamically when they are requested, rather than storing them in arrays. This will reduce the amount of storage and computation required, helping to prevent potential DOS attacks. It might require a slight change in the design of the contract, but it would greatly enhance the security.
