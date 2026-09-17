# [H] Anyone can withdraw underlying from Alchemix

## Summary
Severity: High
Reporter: HonorLt
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L373-L390
Type: audit-issue

## Details
# Anyone can withdraw underlying from Alchemix

## Summary

`withdraw_underlying_to_claim` is unprotected meaning everyone can burn the shares stored in the contract.

## Vulnerability Detail

`withdraw_underlying_to_claim` function does not have any access restriction:
```vyper
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

It trusts the user-supplied parameters to withdraw corresponding assets from Alchemix:
```vyper
@internal
def _withdraw_underlying_from_alchemix(
    _amount_shares: uint256, 
    _receiver: address,
    _min_weth_out: uint256
) -> uint256:
    """
    @notice
        Withdraws _amount_shares to _receiver expecting at least _min_weth_out
    """
    amount_withdrawn: uint256 = IAlchemist(self.alchemist).withdrawUnderlying(
        ALCX_YVWETH,    # _yield_token: address,
        _amount_shares, # _shares: uint256,
        _receiver,      # _recipient: address,
        _min_weth_out   # _min_amount_out: uint256 
    )
    assert amount_withdrawn >= _min_weth_out, "insufficient weth out"
    return amount_withdrawn
```

Based on my understanding, this is really bad because anyone can call this function to burn all the accumulated shares and receive the underlying token. Also, `_min_weth_out` is a parameter that can be supplied any value meaning the slippage protection can be bypassed and the caller can adjust its value and sandwich the interaction for maximum profit.

Maybe I am misinterpreting the situation, and I do not entirely sure how Alchemix works. I have tried to reach the sponsor via DM but received no answer.

## Impact

If my assumptions are right, then the protocol cannot function as intended, because all the received shares from deposits can be instantly burned and sandwiched by anyone.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L373-L390

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L393-L404

## Tool used

Manual Review

## Recommendation

I think this function should have restricted access, e.g. only an operator or position owner based on percentage of shares owned.
