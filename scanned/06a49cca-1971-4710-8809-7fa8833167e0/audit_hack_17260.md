# [H] Lack of `newAddress` Validation in `setValidatorAddress`

## Summary
Severity: High
Reporter: Gigantic Carob Mole
Source: https://github.com/sherlock-audit/2023-11-covalent/blob/main/cqt-staking/contracts/OperationalStaking.sol#L689-L695
Type: audit-issue

## Details
# Lack of `newAddress` Validation in `setValidatorAddress`

krkba
## Summary
There is no validation if `newAddress` in `setValidatorAddress` is a contract address. 
## Vulnerability Detail
If a contract address is provided and it doesn't have a necessary function to receive tokens, tokens could be locked in the contract forever.
## Impact
Loss of funds.
## Code Snippet
https://github.com/sherlock-audit/2023-11-covalent/blob/main/cqt-staking/contracts/OperationalStaking.sol#L689-L695
## Tool used

Manual Review

## Recommendation
