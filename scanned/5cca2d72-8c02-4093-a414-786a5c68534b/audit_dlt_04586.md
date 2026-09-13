# [H] Creation window won't work always.

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-buffer
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/79
Type: sherlock-finding

## Details
silviaxyz

high

# Creation window won't work always.

## Summary
For some cases like holidays, forex markets are closed. 

## Vulnerability Detail
In tests it was tested for timestamp but in the code it is block.timestamp. Also, for non existent records it will retun 0 from config.marketTimes function which does not have validation. For day switches it causes wrong calculations. Also, 

## Impact
Even if we would be in creationWindow for forex options it will still pass the isInCreationWindow check. 

## Code Snippet
https://github.com/sherlock-audit/2022-11-buffer/blob/main/contracts/contracts/core/BufferBinaryOptions.sol#L240-L270

## Tool used

Manual Review

## Recommendation
Update test according to timestamp and use timestamp in the code.
