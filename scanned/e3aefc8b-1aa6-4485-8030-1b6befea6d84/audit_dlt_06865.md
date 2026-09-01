# [H] In `ERC20`, `TotalSupply` is broken

## Summary
Severity: High
Chain: Smart contract
Component: 2022-06-canto
Published: 2022-06-21
Source: https://github.com/code-423n4/2022-06-canto-findings/issues/108
Type: code-finding

## Details
# Lines of code

 https://github.com/Plex-Engineer/lending-market/blob/ab31a612be354e252d72faead63d86b844172761/contracts/ERC20.sol#L33
 https://github.com/Plex-Engineer/lending-market/blob/ab31a612be354e252d72faead63d86b844172761/contracts/ERC20.sol#L95


# Vulnerability details

## Impact
For an obscure reason as it’s not commented, `_totalSupply` is not initialized to 0, leading to an inaccurate total supply, which could easily break integrations, computations of market cap, etc.

## Proof of Concept
If the constructor is called with `_initialSupply = 1000`, then `1000` tokens are minted. The total supply will be `2000`.

## Recommended Mitigation Steps
Remove `_initialSupply`.
