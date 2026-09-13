# [H] MarginDex.swap_margin() allows a delegate to drain the delegator's margin

## Summary
Severity: High
Reporter: whiteh4t9527
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L294
Type: audit-issue

## Details
# MarginDex.swap_margin() allows a delegate to drain the delegator's margin

## Summary
A delegate of a victim (i.e., `self.is_delegate[_account][msg.sender]` is `True`) could swap the victim‘s margin with unlimited slippage and drain all victim's margin.

## Vulnerability Detail
Whenever an user funds his/her margin, his/her delegate account is able to swap the margin asset to another asset through `MarginDex.swap_margin()`. However, the [`swap_margin()` function](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L294) fails to validate the `_min_amount_out` such that a malicious delegate account could use a zero `_min_amount_out` and make profits by providing a UniswapV3 position in advance.

## Impact
An user `P` can drain all margin of another user `Q` if `Q` funds his/her margin and `add_delegate(P)`.

## Code Snippet
```vyper
@external
def swap_margin(
    _account: address,
    _token_in: address,
    _token_out: address,
    _amount_in: uint256,
    _min_amount_out: uint256,
) -> uint256:
    """
    @notice
        Allows a user to easily swap between his margin balances.
    """
    assert (_account == msg.sender) or self.is_delegate[_account][msg.sender], "unauthorized"

    return Vault(self.vault).swap_margin(
        _account, _token_in, _token_out, _amount_in, _min_amount_out
    )
```

## Tool used

Manual Review

## Recommendation
Add slippage protection mechanism.
