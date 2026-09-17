# [H] VADER contains a Fee-On-Transfer

## Summary
Severity: High
Chain: Smart contract
Component: 2021-11-vader
Published: 2021-11-09
Source: https://github.com/code-423n4/2021-11-vader-findings/issues/11
Type: code-finding

## Details
# Handle

jayjonah8


# Vulnerability details

## Impact
The whitepaper says that the Vader token contains a Fee-On-Transfer so in XVader.sol, an attacker may be able to keep calling enter() and leave() while being credited more tokens than the contract actually receives eventually draining it.

## Proof of Concept
1. Attacker deposits 500 Vader
2. Attacker receives credit for 500 while the xVader contract gets the 500 - fee.
3. Attacker calls leave() leaving the contract with a difference of the fee.

https://www.financegates.net/2021/07/28/another-polygon-yield-farm-crashes-to-zero-after-exploit/

https://github.com/code-423n4/2021-11-vader/blob/main/contracts/x-vader/XVader.sol

https://www.vaderprotocol.io/whitepaper


## Tools Used
Manually code review

## Recommended Mitigation Steps
There should be pre and post checks on balances to get the real amount
