# [M] reputation risk via upgradable contracts

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-07-pooltogether
Published: 2021-07-30
Source: https://github.com/code-423n4/2021-07-pooltogether-findings/issues/5
Type: code-finding

## Details
# Handle

gpersoon


# Vulnerability details

## Impact
The contract SwappableYieldSource is upgradable. This means the owner could upgrade and change the contract so any new functionality.
Amongst others the owner could retrieve all the tokens of the Yieldsource and transfer them out.

The project could still be called out for be able to be rug pulled resulting in a reputation risk, see for example:
https://twitter.com/RugDocIO/status/1411732108029181960

## Proof of Concept
//https://github.com/pooltogether/swappable-yield-source/blob/main/contracts/SwappableYieldSource.sol#L19
contract SwappableYieldSource is ERC20Upgradeable, IYieldSource, AssetManager, ReentrancyGuardUpgradeable {

## Tools Used

## Recommended Mitigation Steps
Accept the risk and note it in the comments.
Or change to a non upgradable contract.
