# [M] DAY_IN_BLOCKS is incorrect

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-arcade
Published: 2023-07-25
Source: https://github.com/code-423n4/2023-07-arcade-findings/issues/70
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-07-arcade/blob/main/contracts/external/council/CoreVoting.sol#L15


# Vulnerability details

## Impact
The day in blocks is calculated with the block time as 13.3 seconds in CoreVoting.sol. 
``uint256 public constant DAY_IN_BLOCKS = 6496;``
but since moving to proof of stake block times are fixed to 12 seconds per block https://ethereum.org/en/developers/docs/consensus-mechanisms/pos/#:~:text=Whereas%20under%20proof%2Dof%2Dwork,block%20proposer%20in%20every%20slot

This results in incorrect calculation of the lockDuration and extraVoteTime which is used in setting the total duration a proposal should be active  and also the max vote time.
The time difference can be calculated:

3*24*60*60 / 13.3 = 19488.721804511 (lockDuration with 13.3 seconds)
3*24*60*60 / 12 = 21600 (lockDuration with 12 seconds)
21600-19488.7 = 2111.3
2111.3 * 12 / (60*60) = 7.03 (difference in hours for lockDuration)

5*24*60*60 / 13.3 = 32481.203007519 (extraVoteTime with 13.3 seconds)
5*24*60*60 / 12 = 36000 (extraVoteTime with 12 seconds)
36000 - 32481.2 = 3518.8
3518.8 * 12 / (60*60) = 11.72 (difference in hours extraVoteTime)

By using block time as 13.3 seconds the lockDuration expires 7 hours earlier and the extraVoteTime expires 11.72 hours earlier. Since it is a significant time and affects the proposal and voting duration I consider medium severity to be fair.

## Tools Used
VS code

## Recommended Mitigation Steps
86400 / 12 = 7200
Change the DAY_IN_BLOCKS to 7200
`` uint256 public constant DAY_IN_BLOCKS = 7200; ``


## Assessed type


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-arcade-findings/issues/70_
