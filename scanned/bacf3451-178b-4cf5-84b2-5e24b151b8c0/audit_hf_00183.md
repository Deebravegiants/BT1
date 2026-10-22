# [H] `Vault.balance`

## Summary
Severity: High
Contest weight: 0.2092
Dataset id: 975
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `Vault.balance` function uses the `balanceOfThis` function which scales (“normalizes”) all balances to 18 decimals.
    
    for (uint8 i; i < _tokens.length; i++) {
        address _token = _tokens[i];
        // everything is padded to 18 decimals
        _balance = _balance.add(_normalizeDecimals(_token, IERC20(_token).balanceOf(address(this))));
    }

Note that `balance()`’s second term `IController(manager.controllers(address(this))).balanceOf()` is not normalized. The code is adding a non-normalized amount (for example 6 decimals only for USDC) to a normalized (18 decimals).

## Recommendation
The second term `IController(manager.controllers(address(this))).balanceOf()` must also be normalized before adding it. `IController(manager.controllers(address(this))).balanceOf()` uses `_vaultDetails[msg.sender].balance` which directly uses the raw token amounts which are not normalized.

`balance` and `balanceOfThis` mixes the usage of decimals by alternatingly using `_normalizeDecimals` This can break accounting as well as create opportunities for abuse A consistent usage of `_normalizeDecimals` would mitigate

**BobbyYaxis (yAxis) noted:**

Mitigated in PR 114: <https://github.com/yaxis-project/metavault/pull/114/commits/b3c0405640719aa7d43560f4b4b910b7ba88170b>
