# [H] swap_margin function is highly exposed to reentrancy attacks

## Summary
Severity: High
Reporter: seerether
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L293-L309
Type: audit-issue

## Details
# swap_margin function is highly exposed to reentrancy attacks

## Summary
The swap_margin function in the given code does not have the nonreentrant modifier, which means it is not protected against reentrancy attacks. If this function interacts with external contracts that could trigger reentrancy, it can lead to unexpected behavior and potential loss of funds
## Vulnerability Detail
An attacker's contract can  calls the swap_margin function and provides a malicious token_out address. Inside the swap_margin function, the vulnerable contract transfers tokens from the token_in address to the attacker's contract using an external call. However, before the transfer is completed, the attacker's contract invokes a fallback function in the vulnerable contract.
The fallback function is triggered, and the attacker's contract can execute additional code in the vulnerable contract. The additional code can call the swap_margin function again, triggering a recursive call. This recursive call re-enters the vulnerable contract before the previous call has completed, leading to unexpected behavior and potential manipulation of the contract's state.
## Impact
An attacker can continue exploiting the reentrancy vulnerability to their advantage, potentially draining funds
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L293-L309
## Tool used

Manual Review

## Recommendation
Add the nonreentrant modifier to the swap_margin function. This would prevent multiple reentrant calls to the function within the same transaction
https://github.com/seerether/Unstoppable/blob/527f2d58d6efed57a40084946b34ccbf26a67acc/unstoppablemitigate2#L1
