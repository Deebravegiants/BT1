# [H] Swap can not provide enough tokens to cover the requested reduction

## Summary
Severity: High
Reporter: seerether
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L290-L342
Type: audit-issue

## Details
# Swap can not provide enough tokens to cover the requested reduction

## Summary
In the _reduce_position, there is no verification to ensure that the _reduce_by_amount parameter is approved for transfer from the user's account before calling the swap function.
## Vulnerability Detail
The reduce_position function allows a user to partially close an existing position by selling some of the underlying position_token. However, it does not verify if the amount of position_token received after the swap is sufficient to cover the _reduce_by_amount.
This vulnerability can lead to an unexpected state where the position is reduced by an amount greater than the actual amount received from the swap
## Impact
It will result in a negative position, allowing the user to effectively increase their leverage and potentially exploit the system leading to financial losses.
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L290-L342
## Tool used

Manual Review

## Recommendation
Modify the code in such a way that after calling the swap function in the _reduce_position function, an explicit check amount_out_received >= _reduce_by_amount is added to ensure that the received amount is greater than or equal to the amount being reduced.
This check ensures that the swap operation is successful and provides enough output tokens to cover the requested reduction amount. If the check fails, it will throw an exception and revert the transaction, preventing any incorrect state changes.
https://github.com/seerether/Unstoppable/blob/5bacf8205d7be83c8c5b403724c1109f843bb840/unstoppablemitigate11#L32-L33
