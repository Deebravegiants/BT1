# [H] Tokens is not returned back to the contract when swaps fails

## Summary
Severity: High
Reporter: seerether
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L384-L427
Type: audit-issue

## Details
# Tokens is not returned back to the contract when swaps fails

## Summary
In the _swap function, there is no verification to ensure that the amount_out_received is transferred back to the contract before returning it
## Vulnerability Detail
The vulnerability arises when SwapRouter(self.swap_router).swap is an external call to another contract, and it's assumed that the amount of _token_out received in return is automatically transferred to the current contract (self). However, there's no explicit transfer of the received tokens back to the contract. This can lead to a vulnerability where the amount_out_received is not properly accounted for, potentially allowing an attacker to manipulate the swap and steal funds through reentrancy
This also means that if the swap fails for any reason (e.g., the swap router reverts or encounters an error), the contract will still return the amount_out_received to the caller, even though the contract did not receive those tokens.
## Impact
if the contract expects to receive a certain amount of tokens in exchange for the input tokens, but the swap fails and the tokens are not received, the contract and its users will be at a loss
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L384-L427
## Tool used

Manual Review

## Recommendation
Add the necessary transfer logic in the _swap function to ensure that the amount_out_received is transferred back to the contract before returning it
https://github.com/seerether/Unstoppable/blob/f41fdb1629d6da6fd3006c7f7c82fa0743ca0621/unstoppablemitigate10#L15-L16
