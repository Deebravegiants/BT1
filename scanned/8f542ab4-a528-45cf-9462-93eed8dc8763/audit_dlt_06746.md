# [M] Reputation Risks with `contractOwner`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-03-lifinance
Published: 2022-03-28
Source: https://github.com/code-423n4/2022-03-lifinance-findings/issues/65
Type: code-finding

## Details
# Lines of code

[DiamondCutFacet.sol](https://github.com/code-423n4/2022-03-lifinance/blob/main/src/Facets/DiamondCutFacet.sol)
[WithdrawFacet.sol](https://github.com/code-423n4/2022-03-lifinance/blob/main/src/Facets/WithdrawFacet.sol)
[DexManagerFacet.sol](https://github.com/code-423n4/2022-03-lifinance/blob/main/src/Facets/DexManagerFacet.sol)


# Vulnerability details

## Impact

`contractOwner` has complete freedom to change any functionality and withdraw/rug all assets. Even if well intended the project could still be called out resulting in a damaged reputation [like in this example](https://twitter.com/RugDocIO/status/1411732108029181960)

## Proof of Concept

https://twitter.com/RugDocIO/status/1411732108029181960

## Tools Used

## Recommended Mitigation Steps

Recommend implementing extra safeguards such as:

- Limiting the time period where sensitive functions can be used.
- Having a waiting period before pushed update is executed.
- Using a multisig to mitigate single point of failure in case `contractOwner` private key leaks.
