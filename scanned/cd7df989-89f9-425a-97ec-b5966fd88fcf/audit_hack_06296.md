# [M] User might be forced to pay bad debt of the vault

## Summary
Severity: Medium
Reporter: minhtrng
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L235-L238
Type: audit-issue

## Details
# User might be forced to pay bad debt of the vault

## Summary

Bidder has to pay for bad debt if there is any.

## Vulnerability Detail

Currently, the amount of shares to mint is calculated as the minimum of $valueOfBiddersShares/minimumCollateralization$ and $totalVaultValue/minimumCollateralization-currentDebt$

```py
@internal
@view
def _calculate_amount_to_mint(_amount_shares: uint256) -> uint256:
    return min(self._calculate_mintable_amount(_amount_shares), self._calculate_max_mintable_amount())
```

The odds of the second value being lower seem pretty low, because that would mean the alchemix protocol has somehow broken its collateralization invariant. In this case however, with the current vault implementation, the new bidder would be forced to pay for the incurred debt and hence receive less shares than he should.


## Impact

User pays of debt of others.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L235-L238

## Tool used

Manual Review

## Recommendation
If the case above occurs a user maybe should have the option to get refunded. Just reverting would mean to have the Auction being broken, due to not being settleable, so a solution here is difficult.
