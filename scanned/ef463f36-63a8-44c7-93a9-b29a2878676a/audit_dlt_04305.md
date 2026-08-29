# [M] withdraw() and cancel() opens just in case using nonReentrant or ReentrancyGuard

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-nounsdao
Published: 2022-12-07
Source: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/79
Type: sherlock-finding

## Details
yongkiws

medium

# withdraw() and cancel() opens just in case using nonReentrant or ReentrancyGuard

## Summary
The function has the external and onlyPayerOrRecipient modifiers, which mean that it can be called from outside the contract (i.e., from another contract or from a regular Ethereum account), but only if the caller is either the "payer" or the "recipient" of the tokens.
The function begins by checking if the amount is zero. If it is, it calls the CantWithdrawZero function, which likely reverts the transaction and causes it to fail.he function then retrieves the current balance of the recipient by calling the balanceOf function, passing in the recipient_ address. This balance is stored in the balance variable.

The function then checks if the amount is greater than the recipient's balance. If it is, it calls the AmountExceedsBalance function, which likely reverts the transaction and causes it to fail.

If the amount is not zero and the `amount is not greater than the balance, the functionremainingBalance variable. This is done using the unchecked keyword, which tells

After updating the remainingBalance, the function calls the `safeTransfer function of the token contract, passing in the recipient_ address and the amount as arguments. This function

localrecipient_ and assigns to it therecipient function. This function likely returns the Ethereum address of the recipient of the tokens.

## Vulnerability Detail
In Stream.sol the sponsor() function does not have a reentrancy guard which would allow a re-entering attacker to have a callback to msg.sender. An attacker can make it so that the recipient_ amount is only updated once

## Impact
Summary 

## Code Snippet
```solidity
    function withdraw(uint256 amount) external onlyPayerOrRecipient {
        if (amount == 0) revert CantWithdrawZero();
        address recipient_ = recipient();

        uint256 balance = balanceOf(recipient_);
        if (balance < amount) revert AmountExceedsBalance();

        // This is safe because it should always be the case that:
        // remainingBalance >= balance >= amount.
        unchecked {
            remainingBalance = remainingBalance - amount;
        }
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/79_
