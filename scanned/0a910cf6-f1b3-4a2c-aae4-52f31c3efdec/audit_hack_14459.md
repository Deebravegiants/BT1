# [H] No check on startTime , endTime and stepSize variable which could cause problem in getPriceAt() function

## Summary
Severity: High
Reporter: smbv-1919
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L117
Type: audit-issue

## Details
# No check on startTime , endTime and stepSize variable which could cause problem in getPriceAt() function

medium
## Summary
No check on startTime , endTime and stepSize variable which could cause problem in getPriceAt() function

## Vulnerability Detail
as there is no check on these variables so when getPriceAt() function is called at that time if anyhow (endTime-startTime) value is less than the stepSize variable at that time totalSteps variable would always return 0 during  whole contract  regardless of any time . so if value of stepSize  is greater than (endTime - startTime) somehow then getPriceAt() function would not work properly and always return startPrice throughout the contract and it would always return startPrice when function is called.
## Impact
totalSteps variable would return zero so whenever getPriceAt() is called it would always return the startPrice value so it will be a loss to user who want to purchase NFT as the price  will never get less and they have to purchase NFT in higher price rather than lower price
## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L117 https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122


## Tool used

Manual Review

## Recommendation
there should be require statement which checks that (endPrice - startPrice) is greater than stepSize in constructor so the function works properly.
