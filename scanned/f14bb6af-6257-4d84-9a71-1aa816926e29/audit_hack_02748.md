# [M] Permission to operate funds beyond what is required

## Summary
Severity: Medium
Reporter: innertia
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L74
Type: audit-issue

## Details
# Permission to operate funds beyond what is required

## Summary
Permission to manipulate funds beyond what is necessary leads to unintended loss of funds.
## Vulnerability Detail
The contract sets the USDC Allowance to `type(uint256).max` for both Euler and TrueFi cases.
This gives the authority to withdraw not only the USDC managed by the protocol(Euler, TrueFi), but also the USDC managed by this contract.
This condition is dangerous during the following situations.

* if the protocol is malicious.
* If the protocol has been deprived of its authority by a malicious hacker.  

In particular, `TrueFiStrategy.sol` is dangerous because the withdrawal of USDC from the protocol and the transfer of USDC to the core address are performed by different functions, so there are times when USDC stays in the contract.
The protocol's authority to move USDC should be limited to the portion deposited in the protocol.
## Impact
Lead to loss of funds if protocols are malicious or control is taken by malicious hackers.
## Code Snippet

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L74

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L33

## Tool used

Manual Review

## Recommendation
Use `increaseAllowance` and `decreaseAllowance` functions at appropriate times and amounts.  
(Also, these functions return `bool` value, so it is desirable to receive it properly.)
