# [M] The `Vault.swap_margin()` function can be used to swap to a token which is not whitelisted

## Summary
Severity: Medium
Reporter: 0xbepresent
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L673C5-L673C17
Type: audit-issue

## Details
# The `Vault.swap_margin()` function can be used to swap to a token which is not whitelisted

## Summary

The `Vault.swap_margin()` function can be used to swap to a token which is not in the whitelisted token.

## Vulnerability Detail

The user funds his margin using the [Vault.fund_account()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L673C5-L673C17) or [Vault.fund_account_eth()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L659) functions. Those functions checks if the token is whitelisted in order to allow to fund the margin.

```python
File: Vault.vy
...
665:     assert self.is_whitelisted_token[WETH], "token not whitelisted"
...
679:     assert self.is_whitelisted_token[_token], "token not whitelisted"
...
```

The [Vault.swap_margin()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L728) function helps to swap `token_in` to `token_out`. The problem is that the user can swap to a token which is not in the whitelist, the `Vault.swap_margin()` does not have any validation to ensure that the `token_out` is whitelisted. Since the `Vault.fund_account()` and `Vault.fund_account_eth()` do the whitelist check, the `swap_margin()` should do too.

## Impact

The trader can swap his margin to a token which is not allowed by the protocol.

## Code Snippet

The [Vault.swap_margin()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L728) function:

```python
File: Vault.vy
726: @nonreentrant("lock")
727: @external
728: def swap_margin(
729:     _account: address,
730:     _token_in: address,
731:     _token_out: address,
732:     _amount_in: uint256,
733:     _min_amount_out: uint256,
734: ) -> uint256:
735:     """
736:     @notice
737:         Allows a user to swap his margin balances between differnt tokens.
738:     """
739:     assert self.is_whitelisted_dex[msg.sender] or _account == msg.sender, "unauthorized"
740:     assert _amount_in <= self.margin[_account][_token_in], "insufficient balance"
741: 
742:     self.margin[_account][_token_in] -= _amount_in
743: 
744:     amount_out_received: uint256 = self._swap(
745:         _token_in, _token_out, _amount_in, _min_amount_out
746:     )
747: 
748:     self.margin[_account][_token_out] += amount_out_received
749: 
750:     return amount_out_received
```

The [Vault.fund_account_eth()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L659) and [Vault.fund_account()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L673C5-L673C17) functions:

```python
File: Vault.vy
656: @nonreentrant("lock")
657: @payable
658: @external
659: def fund_account_eth():
660:     """
661:     @notice
662:         Allows a user to fund his WETH margin by depositing ETH.
663:     """
664:     assert self.is_accepting_new_orders, "funding paused"
665:     assert self.is_whitelisted_token[WETH], "token not whitelisted"
666:     self.margin[msg.sender][WETH] += msg.value
667:     raw_call(WETH, method_id("deposit()"), value=msg.value)
668:     log AccountFunded(msg.sender, msg.value, WETH)
669: 
670: 
671: @nonreentrant("lock")
672: @external
673: def fund_account(_token: address, _amount: uint256):
674:     """
675:     @notice
676:         Allows a user to fund his _token margin.
677:     """
678:     assert self.is_accepting_new_orders, "funding paused"
679:     assert self.is_whitelisted_token[_token], "token not whitelisted"
680:     self.margin[msg.sender][_token] += _amount
681:     self._safe_transfer_from(_token, msg.sender, self, _amount)
682:     log AccountFunded(msg.sender, _amount, _token)
```

## Tool used

Manual review

## Recommendation

Check if the `token_out` in the `Vault.swap_margin()` function is whitelisted:

```diff
def swap_margin(
    _account: address,
    _token_in: address,
    _token_out: address,
    _amount_in: uint256,
    _min_amount_out: uint256,
) -> uint256:
    """
    @notice
        Allows a user to swap his margin balances between differnt tokens.
    """
    assert self.is_whitelisted_dex[msg.sender] or _account == msg.sender, "unauthorized"
    assert _amount_in <= self.margin[_account][_token_in], "insufficient balance"
++  assert self.is_whitelisted_token[_token_out], "token out not whitelisted"

    self.margin[_account][_token_in] -= _amount_in

    amount_out_received: uint256 = self._swap(
        _token_in, _token_out, _amount_in, _min_amount_out
    )

    self.margin[_account][_token_out] += amount_out_received

    return amount_out_received
```
