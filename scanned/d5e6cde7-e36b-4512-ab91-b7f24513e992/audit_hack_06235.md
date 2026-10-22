# [H] [H] Not update `amount_claimed` when deposit to existing positions lead to `claimable_for_token` incorrect increased

## Summary
Severity: High
Reporter: oxcm
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L427-L441
Type: audit-issue

## Details
# [H] Not update `amount_claimed` when deposit to existing positions lead to `claimable_for_token` incorrect increased

## Summary

the `amount_claimed` variable in a position is not properly updated when an existing position is deposit with additional funds. This can lead to incorrect calculation of `_claimable_for_token` for the affected position.

## Vulnerability Detail

When an existing position is deposit, the corresponding `shares_owned` value in the Position is correctly increased, but the `amount_claimed` value is not updated to reflect the additional funds. 

This means that the calculation in the `_claimable_for_token` function will be incorrect, as it is based on the `shares_owned` multiplied by the `amount_claimable_per_share`, minus the `amount_claimed`. Since the `amount_claimed` value remains the same after deposit, the calculated `_claimable_for_token` value will be higher than it should be.

## Impact

This vulnerability could result in an incorrect increase in the `_claimable_for_token` value for existing positions that are topped up. it could lead to insufficient funds being available to cover claims, which could result in failed transactions for some token holders.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L427-L441

```vyper=427

@view
@internal
def _claimable_for_token(_token_id: uint256) -> uint256:
    """
    @notice
        Calculates the pending WETH for a given token_id.
    """
    position: Position = self.positions[_token_id]
    if position.is_liquidated:
        return 0
    
    total_claimable_for_position: uint256 = position.shares_owned * self.amount_claimable_per_share / PRECISION
    return total_claimable_for_position - position.amount_claimed

```

## Tool used

Manual Review / ChatGPT PLUS


## Recommendation

updating the `amount_claimed` value in the Position when existing positions are deposit, to ensure that the calculated `_claimable_for_token` value is correct. 

This can be done by adjusting the `amount_claimed` value by the same proportion as the increase in the `shares_owned` value, so that the calculated `_claimable_for_token` value remains consistent.

Or add a new storage variable `last_amount_claimable_per_share` in the Position, and add `claim` before add `shares_issued` to `position.shares_owned` when deposit to existing position. see `Recommendation` in other issue.
