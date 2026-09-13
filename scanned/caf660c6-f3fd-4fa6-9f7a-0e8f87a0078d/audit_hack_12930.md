# [H] Malicious user can prevent it's position from getting liquidated despite exceeding maximum allowed leverage

## Summary
Severity: High
Reporter: Breeje
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L359-L363
Type: audit-issue

## Details
# Malicious user can prevent it's position from getting liquidated despite exceeding maximum allowed leverage

## Summary

Slippage calculation in case of liquidation is calculated On chain with the data earlier known to the User. So malicious user can always force a revert on swapping through uniswap router by sandwiching the transaction in such a way that the protocol always receives less than min output set.

## Vulnerability Detail

1. `liquidate` method calculates `min_amount_out` value on chain.

```solidity
File: Vault.vy

-> liquidate method:

    min_amount_out: uint256 = self._market_order_min_amount_out(
        position.position_token, position.debt_token, position.position_amount
    )

    amount_out_received: uint256 = self._close_position(_position_uid, min_amount_out)

```
[Link to Code](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L359-L363)

```solidity
File: Vault.vy

-> _market_order_min_amount_out method:

    return (
        self._quote_token_to_token(_token_in, _token_out, _amount_in)
        * (PERCENTAGE_BASE - self.liquidate_slippage[_token_in][_token_out])
        / PERCENTAGE_BASE
    )

```
[Link to Code](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L423-L427)

2. A call is made to close the position.

3. Swapping is done through uniswap router using minimum output parameter calculated on chain in step 1.

```solidity
File: Vault.vy

-> _close_position method:

    amount_out_received: uint256 = self._swap(
        position.position_token,
        position.debt_token,
        position.position_amount,
        min_amount_out,
    )


```
[Link to Code](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L252-L257)

4. Malicious User can use a Bot to Sandwich this transaction. Eg: If slippage allowed is let's say 2%, then by sandwiching the transaction bot will try to force more than 2% slippage resulting in the transaction getting reverted at assert shown below.

```solidity
File: Vault.vy

-> _swap method:

    assert (
        token_out_balance_after >= token_out_balance_before + _min_amount_out
    ), "min_amount_out"

```
[Link to Code](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L403-L405)

## Impact

Liquidation can be prevented despite the position exceeding maximum allowed leverage for that market.

## Code Snippet

Used Above

## Tool used

Manual Review

## Recommendation

Do not calculate Slippage on chain during Liquidation.
