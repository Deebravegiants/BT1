# [M] The imported files are outdated

## Summary
Severity: Medium
Reporter: Alexkxs1y
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L9
Type: audit-issue

## Details
# The imported files are outdated

## Summary
The contract does not use the latest version of OpenZeppelin. OpenZeppelin frequently releases updates to address security vulnerabilities discovered in previous versions. By using an outdated version, you might be exposing your smart contract to known security issues.

## Vulnerability Detail
In latest Ownable constructor need to use `initialOwner` address as argument.


## Impact
When updating dependencies, the contract will stop working

## Code Snippet
MeritDutchAuction.sol
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L9

## Tool used

Manual Review

## Recommendation
Use latest version OpenZeppelin contracts
