# [M] ERC20s that block transfer to particular addresses enable DoS/Censorship

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-08-gravitybridge
Published: 2021-09-07
Source: https://github.com/code-423n4/2021-08-gravitybridge-findings/issues/8
Type: code-finding

## Details
# Handle

nascent


# Vulnerability details

Tokens that prevent transfers to particular addresses (most commonly `address(0)` as is the [OpenZeppelin standard](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/aefcb3e8aa4ee8da8e2b7022ffe4dcb57fbb0fdf/contracts/token/ERC20/ERC20.sol#L226)) enables DoS against a batch. If the attacker submits the bad transaction, the relayer wont submit the batch. The attacker never has to worry about the transaction being submitted and paying the fee because the transaction will fail, leaving the relayer stuck with the bill. This can enable MEV between chains by disabling others' ability to close arbitrage between chains by denying them their transfers off the chain.
