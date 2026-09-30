# [H] CircuitBreaker can not incentivize users

## Summary
Severity: High
Contest weight: 0.1954
Dataset id: 16162
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It is stated in the docs that calls to the methods tripBreaker and setValue are incentivized in order to make them work trustlessly and autonomously. However CircuitBreaker.sol has no receive(), no fallback() or payable function which means that there is no way ETH to be sent to the contract.
Because of this, whoever calls tripBreaker or setValue won't receive the expected reward which will lead to discouraging users to call the tripBreaker which is the main functionality of the contract. Thus, instead of not receiving reward, the users will be at loss because of the gas fee. In addition a withdraw method is present in the contract which shows that the initial intention for CircuitBreaker is to be able to receive ETH yet this is not possible.

## Recommendation
Consider enabling CircuitBreaker to receive ETH if you want to use the incentive mechanism mentioned in the docs.
