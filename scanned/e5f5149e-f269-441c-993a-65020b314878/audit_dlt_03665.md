# [M] The user can select the best out of all rerolls (unmitigated issue 4. grouped under M-05)

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-ai-arena-mitigation
Published: 2024-04-16
Source: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/55
Type: code-finding

## Details
# Lines of code

https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/FighterFarm.sol#L424


# Vulnerability details



## Impact
The best out of the entire sequence of reroll results can be selected, instead of having to take a chance at each reroll attempt.

## Proof of Concept
The DNA is set in `FighterFarm.reRoll()` as [uint256(keccak256(abi.encode(tokenId, numRerolls[tokenId])))](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/FighterFarm.sol#L424). This means that the user can calculate the outcomes of all reroll attempts in advance and choose the best one by rerolling until that reroll. This means that it is no longer a reroll but a random sample of fighters offered to the user, from which he can select the best one.

## Recommended Mitigation Steps
The next reroll must not be determined from currently knowable values. This can be achieved by having the admin provide the randomness after a reroll request by the user. This randomness can be in the form of `blockhash(block.number - 1)` set on the admin call.


## Assessed type

Other
