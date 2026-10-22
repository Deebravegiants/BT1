# [H] Any user can trade with the account and funds of any other user

## Summary
Severity: High
Reporter: TheNaubit
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L157
Type: audit-issue

## Details
# Any user can trade with the account and funds of any other user

## Summary
Any user of the protocol can trade with the funds holded by another account in the protocol and also they can manage every position any account holds.

## Vulnerability Detail
Trading functions running in the Margin Dex are called in the `MarginDex` contract and there they are protected by the check `assert (_account == msg.sender) or self.is_delegate[_account][msg.sender], "unauthorized"`, which prevents non-authorized users to trade with the funds of other accounts.

But those functions are basically calling the trading functions inside the`Vault` contract; which are `external` and they don't have any check to verify the user calling them is authorized.

## Impact
This affects to all the trading functions, allowing to anyone to use other users' funds as they want and to control all their positions as they wish. They could even open bad positions in other users' accounts so their own positions are beneficiated by that.

## Code Snippet
Affected functions:
- `open_position`: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L157
- `close_position`: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L227
- `reduce_position`: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L290
- `add_margin`: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L503
- `remove_margin`: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L528

## Tool used
Manual Review

## Recommendation
Change the functions' visibility or add a check like the ones added to the `MarginDex` contract:
```vyper
assert (_account == msg.sender) or self.is_delegate[_account][msg.sender], "unauthorized"
```
