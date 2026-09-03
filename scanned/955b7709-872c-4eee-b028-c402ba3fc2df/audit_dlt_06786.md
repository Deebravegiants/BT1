# [H] backdoor in `withdrawRedundant`

## Summary
Severity: High
Chain: Smart contract
Component: 2022-01-insure
Published: 2022-01-13
Source: https://github.com/code-423n4/2022-01-insure-findings/issues/252
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

The `Vault.withdrawRedundant` has wrong logic that allows the admins to steal the underlying vault token.

```solidity
function withdrawRedundant(address _token, address _to)
     external
     override
     onlyOwner
{
     if (
          _token == address(token) &&
          balance < IERC20(token).balanceOf(address(this))
     ) {
          uint256 _redundant = IERC20(token).balanceOf(address(this)) -
               balance;
          IERC20(token).safeTransfer(_to, _redundant);
     } else if (IERC20(_token).balanceOf(address(this)) > 0) {
          // @audit they can rug users. let's say balance == IERC20(token).balanceOf(address(this)) => first if false => transfers out everything
          IERC20(_token).safeTransfer(
               _to,
               IERC20(_token).balanceOf(address(this))
          );
     }
}
```

#### POC
- Vault deposits increase as `Vault.addValue` is called and the `balance` increases by `_amount` as well as the actual `IERC20(token).balanceOf(this)`. Note that `balance == IERC20(token).balanceOf(this)`
- Admins call `vault.withdrawRedundant(vault.token(), attacker)` which goes into the `else if` branch due to the balance inequality condition being `false`. It will transfer out all `vault.token()` amounts to the attacker.

## Impact
There's a backdoor in the `withdrawRedundant` that allows admins to steal all user deposits.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-01-insure-findings/issues/252_
