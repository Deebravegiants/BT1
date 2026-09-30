# [H] Attacker can call `Vault.withdraw_underlying_to_claim()` with no slippage protection to cause loss of funds

## Summary
Severity: High
Reporter: Ruhum
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L393-L404
Type: audit-issue

## Details
# Attacker can call `Vault.withdraw_underlying_to_claim()` with no slippage protection to cause loss of funds

## Summary
An attacker can call the `withdraw_underlying_to_claim()` function without adding slippage protection to cause a loss of funds for every depositor. 

## Vulnerability Detail
The `withdraw_underlying_to_claim()` function is callable by anyone. The caller can use the `_min_weth_out` parameter to add slippage protection. By setting that value to `0` the tx will likely be sandwiched by MEV bots causing the vault to receive less WETH than it should for the number of burned shares. 

## Impact
Partial loss of funds for every depositor because shares are burned for less WETH than they are actually worth.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L393-L404
```python
@external
def withdraw_underlying_to_claim(_amount_shares: uint256, _min_weth_out: uint256):
    """
    @notice
        Withdraws _amount_shares and _min_weth_out from Alchemix to be distributed
        to token holders.
        The WETH is held in this contract until it is `claim`ed.
    """
    amount_withdrawn: uint256 = self._withdraw_underlying_from_alchemix(_amount_shares, self, _min_weth_out)
    self._mark_as_claimable(amount_withdrawn)

    log Claimable(amount_withdrawn)
```

## Tool used

Manual Review

## Recommendation
