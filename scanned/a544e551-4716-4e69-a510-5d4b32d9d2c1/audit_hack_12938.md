# [H] The liquidatable position can be closed before someone liquidates it causing that the liquidation penalty to be evaded

## Summary
Severity: High
Reporter: 0xbepresent
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L227
Type: audit-issue

## Details
# The liquidatable position can be closed before someone liquidates it causing that the liquidation penalty to be evaded

## Summary

The liquidatable position can be closed using the [Vault.close_position()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L227) function causing the evasion of the [liquidation penalty](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L368-L373).


## Vulnerability Detail

The [Vault.liquidate()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L346) function helps to liquidate a liquidatable position. The function makes the next executions:
1. It calculates the [min_amount_out](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L359) based on the position debt and position amount.
2. Then [it closes the position](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L363) using the `Vault._close_position()` function.
3. If there is enough amount_out_received, [it charges a penalty](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L368-L373) to the account's margin.

The problem is that the user account can call directly the [Vault.close_position()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L227) before someone liquidates him. I created the next test where the position is closed before someone can liquidates it:

```python
# tests/vault/test_liquidate.py
# $ pytest -k "test_close_position_before_get_liquidated"
def test_close_position_before_get_liquidated(
    vault, owner, alice, weth, usdc, eth_usd_oracle
):
    """
    Close the position before it get liquidated so the penalty can be evaded
    """
    #
    # 1. Open a position
    #
    position_uid, _ = open_position(vault, owner, weth, usdc)
    eth_usd_oracle.set_answer(1234_0000_0000)
    # we have have a margin of 10USDC, borrow 90 and buy for 100 thus
    # our effective leverage is 10 as we have 10 times our margin-value in ETH
    assert vault.effective_leverage(position_uid) == 10
    eth_usd_oracle.set_answer(1135_0000_0000)
    #
    # 2. Position is liquidable right now
    #
    assert vault.effective_leverage(position_uid) == 51
    assert vault.is_liquidatable(position_uid) == True
    #
    # 3. Close position before someone liquidates it so the penalty can be evaded
    #
    vault.close_position(position_uid, 0)
    assert vault.positions(position_uid)[1:] == (
        "0x0000000000000000000000000000000000000000",
        "0x0000000000000000000000000000000000000000",
        0,
        0,
        "0x0000000000000000000000000000000000000000",
        0,
    )
```

## Impact

The position can be closed before someone can liquidates it causing the user account can evade the liquidation penalty so those penalties are lost.

## Code Snippet

- The [Vault.liquidate()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L346) function.
- The [Vault.close_position()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L227) function.

## Tool used

Manual review

## Recommendation

The external [Vault.close_position()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L227) function should be called only if the position is not liquidatable.

```diff
def close_position(_position_uid: bytes32, _min_amount_out: uint256) -> uint256:
    assert self.is_whitelisted_dex[msg.sender], "unauthorized"
++  assert not self._is_liquidatable(_position_uid), "in liquidation" 
    return self._close_position(_position_uid, _min_amount_out)
```
