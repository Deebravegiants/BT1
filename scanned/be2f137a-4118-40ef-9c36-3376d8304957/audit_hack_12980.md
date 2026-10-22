# [H] First user will get more shares

## Summary
Severity: High
Reporter: Bauer
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L899
Type: audit-issue

## Details
# First user will get more shares

## Summary
First user will get more shares
## Vulnerability Detail
The function `_amount_to_lp_shares()` converts a token amount into the corresponding number of LP shares, taking into account the existing shares and the precision requirements.
Inside the function , it first checks if there are any existing shares for the token. If not, it returns the token amount multiplied by PRECISION (a constant representing the desired precision). If there are existing shares, it retrieves the amount of wei per share using the _amount_per_safety_module_lp_share function. Then, it calculates the new shares by multiplying the token amount by PRECISION twice (to account for the desired precision) and dividing it by the wei per share.
```solidity
def _amount_to_lp_shares(
    _token: address, _amount: uint256, _is_safety_module: bool
) -> uint256:
    if _is_safety_module:
        # initial shares == wei
        if self.safety_module_lp_total_shares[_token] == 0:
            return _amount * PRECISION

        wei_per_share: uint256 = self._amount_per_safety_module_lp_share(_token)
        new_shares: uint256 = _amount * PRECISION * PRECISION / wei_per_share
        return new_shares

    else:  # base_lp
        # initial shares == wei
        if self.base_lp_total_shares[_token] == 0:
            return _amount * PRECISION

        wei_per_share: uint256 = self._amount_per_base_lp_share(_token)
        new_shares: uint256 = _amount * PRECISION * PRECISION / wei_per_share
        return new_shares

```
Let me deep into the function `_amount_per_safety_module_lp_share()`. If the token's decimals value is 18 ，the return valule will be x*1e36. Hence , `new_shares` will be y*1e18. `new_shares: uint256 = _amount * PRECISION * PRECISION / wei_per_share`. However, if there are not existing shares, the return value will be z*1e36  `_amount * PRECISION`.If the user is the first user, they will receive LP shares that are multiplied by 1e18 (10^18).

```solidity
def _amount_per_safety_module_lp_share(_token: address) -> uint256:
    return (
        self._safety_module_total_amount(_token)
        * PRECISION
        * PRECISION
        / self.safety_module_lp_total_shares[_token]
    )

```

## Impact
User will get more shares.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L899

## Tool used

Manual Review

## Recommendation
If there are not existing shares,return amount.
