# [H] `withdraw_underlying_to_claim` can be used by an attacker for sandwitch attacks.

## Summary
Severity: High
Reporter: psy4n0n
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L394
Type: audit-issue

## Details
# `withdraw_underlying_to_claim` can be used by an attacker for sandwitch attacks.

## Summary

The `withdraw_underlying_to_claim` function can be called by anyone and also has `_min_weth_out` which is controlled in the parameters, this function can be used to withdraw underlying tokens from alchemix with _min_weth_out low, so that an attacker can sandwitch this transaction and the vault would loose some tokens.

## Vulnerability Detail

The function `withdraw_underlying_to_claim` is used to withdraw the underling tokens from alchemix to the vault. The function calls `IAlchemist(self.alchemist).withdrawUnderlying` internally with the receiver set to the vault address and the `_min_weth_out` is controlled by the attacker.

Assuming a scenario where the fund_receiver repays the loan and the tokens are available to be withdrawn and the amount is large enough. Then the attacker can call `withdraw_underlying_to_claim` with some less gas amount and sandwich it with a transaction. This would lead to the vault receiving less token (as the minimum value is set by attacker). It can be argued that alchemix would revert the transaction if the loss is greater than the maxLoss set in alchemix, but the attacker can still gain and the legitimate users would still loose some amount of ETH that is set on alchemix by `setMaximumLoss` function.  This value can 

## Impact

Partial loss of user funds.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L394

```vyper
def withdraw_underlying_to_claim(_amount_shares: uint256, _min_weth_out: uint256):
    """
    @notice
        Withdraws _amount_shares and _min_weth_out from Alchemix to be distributed
        to token holders.
        The WETH is held in this contract until it is `claim`ed.
        @audit can be used for sandwitch attacks
    """
    amount_withdrawn: uint256 = self._withdraw_underlying_from_alchemix(_amount_shares, self, _min_weth_out)
    self._mark_as_claimable(amount_withdrawn)

    log Claimable(amount_withdrawn)
```

## Tool used

Manual Review

## Recommendation

This function can be made callable only by users/owner.
