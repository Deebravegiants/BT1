# [H] `withdraw_underlying_to_claim` is callable by anybody; can be abused

## Summary
Severity: High
Reporter: ABA
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L393-L404
Type: audit-issue

## Details
# `withdraw_underlying_to_claim` is callable by anybody; can be abused

## Summary

the function `withdraw_underlying_to_claim` is missing a check that the caller should be an operator (or other privileged role).

## Vulnerability Detail

`withdraw_underlying_to_claim` withdraws _amount_shares and _min_weth_out from Alchemix to be distributed to token holders on claim. 

Because anybody can execute `withdraw_underlying_to_claim`, a malicious actor can constantly call it, effectively invalidating any advantage that the `Vault` may have with using `Alchemix`.

## Impact

The whole advantage of using `Alchemix` for self paying loans is invalidated, effectively removes it from the contract.

The collateral itself can only be extracted by each token holder, but the `Alchemix` position is destroyed.

## Code Snippet

[Function](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L393-L404)

```Python
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

Add operator requirement for `withdraw_underlying_to_claim`. 
```Python
@@ -398,6 +398,7 @@ def withdraw_underlying_to_claim(_amount_shares: uint256, _min_weth_out: uint256

+    assert self.is_operator[msg.sender], "unauthorized"
     amount_withdrawn: uint256 = self._withdraw_underlying_from_alchemix(_amount_shares, self, _min_weth_out)
     self._mark_as_claimable(amount_withdrawn)
```

ERC721 token holders can still withdrawal their own positions via the `claim` function, respecting the protocol public facing contract/scope.
