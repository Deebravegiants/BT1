# [M] User influence on DNA via `fighters.length` in `mintFromMergingPool()` (unmitigated issue 3. grouped under M-05)

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-ai-arena-mitigation
Published: 2024-04-16
Source: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/54
Type: code-finding

## Details
# Lines of code

https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/FighterFarm.sol#L366


# Vulnerability details



## Impact
The user can wait for an appropriate `fighters.length` to get a better DNA when minting from the merging pool.

## Proof of Concept
A winning user can call `MergingPool.claimRewards()`, which [calls `FighterFarm.mintFromMergingPool()`](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/MergingPool.sol#L162). Here the DNA is set as [`uint256(keccak256(abi.encode(to, fighters.length)))`](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/FighterFarm.sol#L366). This means that the user can choose to call `claimRewards()` when `fighters.length` is such that the DNA gives better attributes.

## Recommended Mitigation Steps
Note that there is also an issue with using `to` in setting the DNA (the mitigation error from the fix of #578). This mitigation fixes both of these.
Set the DNA as `blockhash(block.number - 1)`. This must be in a call from the admin, otherwise the user could wait for a good blockhash. Then in a second call by the user assign the fighter to the user, either through direct minting to the user, or mint the fighter to an escrow (e.g. FighterFarm itself) and then have the user transfer it to himself in the second call.


## Assessed type

Other
