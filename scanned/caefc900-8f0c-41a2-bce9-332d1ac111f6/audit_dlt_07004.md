# [M] Profile creation can be frontrun

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-aave-lens
Published: 2022-02-14
Source: https://github.com/code-423n4/2022-02-aave-lens-findings/issues/26
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-02-aave-lens/blob/aaf6c116345f3647e11a35010f28e3b90e7b4862/contracts/libraries/PublishingLogic.sol#L50


# Vulnerability details

## Impact
The `LensHub/PublishingLogic.createProfile` function can be frontrun by other whitelisted profile creators.
An attacker can observe pending `createProfile` transactions and frontrun them, own that handle, and demand ransom from the original transaction creator.

## Recommended Mitigation Steps
Everyone needs to use flashbots / private transactions but it might not be available on the deployed chain.
A commit/reveal scheme for the handle and the entire profile creation could mitigate this issue.
