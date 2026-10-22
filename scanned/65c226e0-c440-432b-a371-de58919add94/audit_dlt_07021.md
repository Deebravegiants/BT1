# [M] M-02 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-06-ambire-mitigation
Published: 2023-06-21
Source: https://github.com/code-423n4/2023-06-ambire-mitigation-findings/issues/9
Type: code-finding

## Details
# Lines of code

https://github.com/AmbireTech/ambire-common/blob/455a8057e1e6edae48903fc9d116591b22fbf1c2/contracts/AmbireAccount.sol#L113-L119


# Vulnerability details

## Description
The mitigation recommendation is not right. To understand the issue I strongly recommend the lecture of [this article](https://ronan.eth.link/blog/ethereum-gas-dangers/#workaround-against-insuficient-gas-griefing-attack). In particular, sections ["Insufficient Gas Griefing Attack"](https://ronan.eth.link/blog/ethereum-gas-dangers/#3-insufficient-gas-griefing-attack) and ["Workaround Against “Insuficient Gas Griefing attack”"](https://ronan.eth.link/blog/ethereum-gas-dangers/#workaround-against-insuficient-gas-griefing-attack).

The issue reported state that we can fail the call due to run out of gas given 63/64 rule introduced by EIP-150, and then succeed our execution with 1/64 left gas. In this way the try catch call will fail but the nonce will still increase.

This is true, but the mitigation recommended it is not ok. According to [SWC-126 there are only two ways to prevent an insufficient gas griefing attack](https://swcregistry.io/docs/SWC-126) in cases similar to ambire wallet:
1. Only allow trusted users to relay transactions.
2. Require that the forwarder provides enough gas.

Given that option 2 is done through `tryCatchLimit` (wrongly, an it reported as an issue **`tryCatchLimit`  can forward less than the specified gasLimit due to EIP-150**), we can only:
* Remove `tryCatch` function
* Add a modifier to `tryCatch` to ensure it is only executed by a trusted relayer (given that this call can only be done through next path `executeBySender --> executeBatch --> executeCall --> tryCatch`), checking `tx.origin`, even though it is usually rejected to be used, might be advisable, or a previous check in `executeCall` if we are trying to execute this function.




## Assessed type

Other
