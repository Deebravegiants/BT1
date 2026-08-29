# [M] Malicious user can trigger another user’s removal

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-06-realitycards
Published: 2021-06-16
Source: https://github.com/code-423n4/2021-06-realitycards-findings/issues/100
Type: code-finding

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

By allowing anyone to call removeUserFromOrderbook instead of only Market::newRental or Treasury::withdrawDeposit or collectRentUser which may result in foreclosures and hence may need to trigger user removal, a malicious user can trigger another's removal by front-running the user's deposit or exit actions to prevent foreclosure.

Impact: Alice is about to be foreclosed but has submitted a deposit transaction. Evil Eve notices Alice’s pending foreclosure and front-runs her deposit to trigger removeUserFromOrderbook. Alice is removed from the order book and markets.

## Proof of Concept

https://github.com/code-423n4/2021-06-realitycards/blob/86a816abb058cc0ed9b6f5c4a8ad146f22b8034c/contracts/RCOrderbook.sol#L572-L579


## Tools Used

Manual Analysis

## Recommended Mitigation Steps

Restrict access to this function only to those functions that may cause user foreclosure and hence need to remove user from order book.
