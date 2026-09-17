# [H] Giddy incident: The DeFi protocol Giddy’s GiddyVaultV3 contract was exploited, resulting in a loss of approximately $1.3 million. The attack was c

## Summary
Severity: High
Target: Giddy
Loss: $ 1,300,000
Attack method: Smart Contract Vulnerability
Published: 2026-04-23
Source: https://x.com/DefimonAlerts/status/2047334517535642024
Type: slowmist-incident

## Details
The DeFi protocol Giddy’s GiddyVaultV3 contract was exploited, resulting in a loss of approximately $1.3 million. The attack was caused by a design flaw in its authorization validation logic. When using the EIP-712 signature scheme, the contract only validated part of the data within the SwapInfo structure, failing to cover critical parameters such as aggregator, fromToken, toToken, and amount, leading to incomplete signature coverage. The attacker exploited this flaw by replaying a valid signature and crafting malicious transaction parameters: replacing fromToken with the strategy’s LP tokens, setting the aggregator to a contract controlled by the attacker, substituting toToken with a malicious token, and setting the transaction amount to the maximum value. Since these key fields were not included in the signature verification scope, the contract accepted the transaction as valid and executed it. As a result, the attacker successfully transferred out protocol assets, causing a loss of approximately $1.3 million.
