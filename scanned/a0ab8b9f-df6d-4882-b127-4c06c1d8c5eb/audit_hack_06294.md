# [H] Marking claims through collateral withdrawal results in unfair claim distribution

## Summary
Severity: High
Reporter: hickuphh3
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L373-L419
Type: audit-issue

## Details
# Marking claims through collateral withdrawal results in unfair claim distribution

## Summary
Withdrawn collateral from marked claims is no longer used to generate yield, but remains accounted to be so, resulting in unfair yield distribution.

## Vulnerability Detail
Yield is marked as claimable by withdrawing collateral from the `alchemist`. This means that the withdrawn collateral resides in the `vault` contract and isn't used for generating yield. However, it is counted towards the holders' shares when splitting yield, resulting in an unfair distribution.
 
Consider the following scenario:
1) Alice deposits 1 WETH (0.5 alETH is minted), gets 100 shares
2) 0.25 alETH is repaid => 0.5 ETH is marked as claimable, withdrawn and sent to the contract
3) Bob deposits 1 WETH (0.5 alETH is minted), gets 100 shares

At this point, only 1 + 1 - 0.5 = 1.5 WETH is in Alchemix, of which 1/3 belongs to Alice, the remaining 2/3 belongs to Bob. Hence, Bob should be entitled to 2/3 of all subsequent yields, but the current implementation splits the yield equally. Bob is therefore shortchanged.

## Impact
Unfair yield distibution.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L373-L419

## Tool used
Manual Review

## Recommendation
Instead of withdrawing collateral, consider minting debt as yield instead. The distribution becomes fair:

1. Alice put in 1 ETH (borrow 0.5 alETH)
2. 0.25 alETH repaid => system mints 0.25 alETH, marks it payable, entirely to Alice.
3.  Bob put in 1 ETH (borrow 0.5 alETH) => total debt remains at 1 alETH

Both Alice and Bob's WETH deposits remain entirely in the system, and can be liquidated to claw back their funds. For instance, if Alice liquidates, her 1 WETH would pay half of the system debt (0.5 alETH), and would be getting back 0.5 ETH (+0.25 alETH yield).
