# [M] Withdraws have no access control and allow for bad slippage control

## Summary
Severity: Medium
Reporter: minhtrng
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L393-L404
Type: audit-issue

## Details
# Withdraws have no access control and allow for bad slippage control

## Summary

A malicious actor can perform withdraw to claim without slippage control to cause a loss to the share holders.

## Vulnerability Detail

The function `Vault.withdraw_underlying_to_claim` is meant to be permissionless according to the code documentation. However, this allows anyone to call the function with the parameter `_min_weth_out == 0`:

```py
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

This should be able to cause a loss of assets under certain circumstances, evidenced by the fact that both Alchemix and Yearn have slippage control parameters for withdrawals in the first place. However, I do not have a sufficient in-depth understanding of either of these protocols to map out the circumstances and possibly more critical attack paths that allow for the theft of the funds. Hence I will categorize the severity as medium (griefing that causes harm, but has no financial benefit for the attacker).

## Impact

Possible loss of assets due to no slippage control.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L393-L404

## Tool used

Manual Review

## Recommendation
Options:
1. Try to heuristically determine a lower bound for the `_min_weth_out` parameter.
2. Restrict the access to the function to NFT holders and maybe vault owner only, as they have an incentive to not perform bad calls.
