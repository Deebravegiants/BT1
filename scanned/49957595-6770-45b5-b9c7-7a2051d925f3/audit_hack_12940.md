# [H] If the protocol is in defensive mode `is_accepting_new_orders is False` the users are unable to fund their account and to be unable to add margin to their positions

## Summary
Severity: High
Reporter: 0xbepresent
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L266
Type: audit-issue

## Details
# If the protocol is in defensive mode `is_accepting_new_orders is False` the users are unable to fund their account and to be unable to add margin to their positions

## Summary

When a position is in bad debt, all the protocol is set defensive mode 'is_accepting_new_orders is False' causing that users can't fund their margin and to be unable to cover their margin positions, so this situation obligate them to reduce their positions in order to not be liquidatable.

## Vulnerability Detail

The protocol can be in [defensive mode](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L266) when one position enters in bad debt. Once the protocol is in defensive mode `is_accepting_new_orders is False` the next functions are disabled:

- [Vault.open_position()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L171)
- [Vault.fund_account_eth()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L664)
- [Vault.fund_account()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L673)
- [Vault.provide_liquidity_eth()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L767C5-L767C26)
- [Vault.provide_liquidity()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L786C5-L786C22)

The problem is that an user can't add funds to their margin account using the [Vault.fund_account()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L673) or [Vault.fund_account_eth()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L664) functions. So this causes that the user may not have margin to add to their position using the [Vault.add_margin()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L503C5-L503C15) function. This situation obligate them to reduce their position in order to not be liquidatable.

I created a test where the `fund_account()` function is not available once the system enters in defensive mode 'is_accepting_new_orders is False'

```python
# tests/vault/test_close_position.py
# $ pytest -k "test_close_position_in_bad_debt_deactivates_accepting_new_orders_and_fund_account"
def test_close_position_in_bad_debt_deactivates_accepting_new_orders_and_fund_account(
    vault, usdc, weth, owner, alice
):
    """
    When a position is in bad debt, all the protocol is set defensive mode 'is_accepting_new_orders is False'
    causing that users can't fund their margin and be unable to cover their margin positions, so this situation
    obligate them to reduce their positions in order to not be liquidatable.
    """
    #
    # 1. Create the position and put it in bad debt, so the is_accepting_new_orders is desactivated
    #
    position_uid, _ = open_position(vault, owner, weth, usdc)
    assert vault.is_accepting_new_orders()
    vault.positions(position_uid)
    vault.close_position(position_uid, 0)  # 0 out
    bad_debt_after = vault.bad_debt(usdc)
    assert bad_debt_after > 0
    assert vault.is_accepting_new_orders() is False
    #
    # 2. The fund account is not available any more
    #
    with boa.env.prank(alice):
        with boa.reverts("funding paused"):
            vault.fund_account(usdc, 1)
```

## Impact

When the system is in `defensive mode` the users are unable to fund their accounts, then the users are obligated to reduce their position in order the avoid the liquidation. Users can lost their positions if they enter in panic and they can not fund their margin accounts.

## Code Snippet

- The [Vault._close_position()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L233) function which sets the system in [defensive mode](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L266) if there is a bad debt.

## Tool used

Manual review

## Recommendation

The easier solution is to avoid liquidations while the system is in `defensive mode`.
