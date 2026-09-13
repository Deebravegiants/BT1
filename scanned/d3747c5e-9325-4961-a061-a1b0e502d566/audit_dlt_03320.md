# [H] logic calls can steal tokens

## Summary
Severity: High
Chain: Smart contract
Component: 2021-08-gravitybridge
Published: 2021-09-08
Source: https://github.com/code-423n4/2021-08-gravitybridge-findings/issues/25
Type: code-finding

## Details
# Handle

0xito


# Vulnerability details

## Impact
attacker can send a logic call that performs a `token.approve(attackerAddress, type(uint256).max)` using the `submitLogicCall` function.

afterwards, they can steal all tokens from the bridge using `token.safetransferfrom(bridge, attacker, amount)`.

## Proof of Concept
- `submitLogicCall` with `token.approve(attackerAddress, type(uint256).max)` 
- call `token.safetransferfrom(bridge, attacker, amount)`

## Tools Used

## Recommended Mitigation Steps
disallow calls to the bridge contract, or to any token/NFT contracts that the bridge owns tokens of (`token.balanceOf(address(this)) > 0`).
